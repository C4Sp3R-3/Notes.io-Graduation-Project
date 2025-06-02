# Database imports
from contextlib import contextmanager
import mysql.connector
from mysql.connector import pooling
import pyodbc
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, Dict, Any, List, Union
from logger import logger
from config import Config
from pymongo import MongoClient
from pymongo.errors import PyMongoError

db_connection = None

class DatabaseConnection:
    """Abstract base for database connections"""
    def execute_query(self, query: str, args=None, dictionary: bool = False):
        raise NotImplementedError
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        raise NotImplementedError

class MySQLConnection(DatabaseConnection):
    """MySQL database connection handler"""
    
    def __init__(self, config: Config):
        self.config = {
            "host": config.DATABASE_HOST,
            "user": config.DATABASE_USERNAME,
            "password": config.DATABASE_PASSWORD,
            "database": config.DATABASE_NAME,
            "autocommit": False,  # Explicit transaction control
            "charset": 'utf8mb4',
            "collation": 'utf8mb4_unicode_ci'
        }
        try:
            self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="mypool", 
                pool_size=10,
                pool_reset_session=True,
                **self.config
            )
            logger.info("MySQL connection pool initialized")
        except mysql.connector.Error as e:
            logger.error(f"Failed to create MySQL connection pool: {e}")
            raise

    @contextmanager
    def get_connection(self):
        """Context manager for MySQL connections"""
        connection = None
        try:
            connection = self.connection_pool.get_connection()
            yield connection
        finally:
            if connection:
                connection.close()

    def execute_query(self, query: str, args: tuple = (), dictionary: bool = False) -> Optional[Union[List, int]]:
        """Execute MySQL query with proper error handling"""
        with self.get_connection() as connection:
            cursor = None
            try:
                cursor = connection.cursor(dictionary=dictionary)
                cursor.execute(query, args)
                
                if cursor.description:
                    result = cursor.fetchall()
                    if len(result)==1:
                        return result[0]
                else:
                    result = cursor.rowcount
                    connection.commit()
                
                return result
                
            except mysql.connector.IntegrityError as e:
                logger.warning(f"MySQL integrity error: {e}")
                connection.rollback()
                return None
            except mysql.connector.Error as e:
                logger.error(f"MySQL error: {e}")
                connection.rollback()
                return None
            finally:
                if cursor:
                    cursor.close()
                    connection.commit()

class MongoDBConnection:
    """MongoDB handler for the 'Note' collection"""

    def __init__(self):
        try:
            self.client = MongoClient(Config.MONGODB_URI)
            self.db = self.client[Config.MONGODB_DATABASE]
            self.collection = self.db[Config.MONGODB_NOTE_COLLECTION]
            logger.info("MongoDB 'Note' collection ready.")
        except PyMongoError as e:
            logger.error(f"MongoDB connection error: {e}")
            raise

    @contextmanager
    def get_connection(self):
        try:
            yield self.collection
        finally:
            pass

    def insert(self, data: Dict[str, Any]) -> Optional[str]:
        """Insert a note and return its ID."""
        try:
            result = self.collection.insert_one(data)
            return str(result.inserted_id)
        except PyMongoError as e:
            logger.error(f"Insert failed: {e}")
            return None

    def update(self, data: Dict[str, Any]) -> Optional[int]:
        """Update a note by _id. Expects '_id' in the data."""
        try:
            note_id = data.get("_id")
            if not note_id:
                logger.warning("Missing '_id' in update payload.")
                return None
            _id = note_id if isinstance(note_id, str) else note_id
            data_to_update = {k: v for k, v in data.items() if k != "_id"}
            result = self.collection.update_one({"_id": _id}, {"$set": data_to_update})
            return result.modified_count
        except PyMongoError as e:
            logger.error(f"Update failed: {e}")
            return None

    def delete(self, note_id: str) -> Optional[int]:
        """Delete a note by ID."""
        try:
            result = self.collection.delete_one({"_id": note_id})
            return result.deleted_count
        except PyMongoError as e:
            logger.error(f"Delete failed: {e}")
            return None

    def get(self, note_id: str) -> Optional[Dict[str, Any]]:
        """Get a single note by ID."""
        try:
            result = self.collection.find_one({"_id": note_id})
            return result
        except PyMongoError as e:
            logger.error(f"Get failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Invalid note ID: {e}")
            return None

    def find(self, filter: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Find notes by filter (default: all)."""
        try:
            return list(self.collection.find(filter or {}))
        except PyMongoError as e:
            logger.error(f"Find failed: {e}")
            return []

def create_database_connection(config: Config) -> DatabaseConnection:
    """Factory function to create appropriate database connection"""
    return MySQLConnection(config)

def get_db() -> DatabaseConnection:
    """Get database connection"""
    return create_database_connection(Config)

def get_user_from_session(session_cookie: str) -> Optional[Dict]:
    """Get user data from session cookie"""
    if not session_cookie:
        return None
    
    try:
        query = """
            SELECT u.id, u.username, u.email, u.is_mfa_enabled,
                   s.valid, TIMESTAMPDIFF(MINUTE, s.last_active, NOW()) AS inactive_minutes
            FROM users u
            INNER JOIN sessions s ON u.id = s.user_id
            WHERE s.session_token = %s
        """
        result = get_db().execute_query(query, (session_cookie,), True)
        return result if result else None
    except Exception as e:
        logger.error(f"Session validation error: {e}")
        return None
            

# MongoDB local test
if __name__ == "__main__":
    db = MongoDBConnection()
    print(db.find({'_id': 'note-id', 'ownerId': 'user-id' }))

