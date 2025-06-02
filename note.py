from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid
import json

@dataclass
class Note:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    title: str = field(default="")
    content_json: str = field(default="{}")
    owner_id: Optional[str] = None
    public_read: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def from_json(self, data) -> dict:
        return json.loads(data)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "title": self.title,
            "content_json": self.content_json,
            "owner_id": self.owner_id,
            "public_read": self.public_read,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @staticmethod
    def from_dict(data: dict) -> "Note":
        return Note(
            id=uuid.UUID(data.get("id")) if data.get("id") else uuid.uuid4(),
            title=data.get("title", ""),
            content_json=data.get("content_json", "{}"),
            owner_id=data.get("owner_id"),
            public_read=data.get("public_read", False),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.utcnow(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else datetime.utcnow()
        )