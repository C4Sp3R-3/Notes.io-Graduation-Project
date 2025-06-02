import os
from dotenv import load_dotenv

load_dotenv("./.env")

class Config:
    """Centralized configuration class"""
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
    MAX_COOKIE_LIFETIME = int(os.getenv('MAX_COOKIE_LIFETIME', 3600))  # seconds
    DATABASE_HOST = os.getenv('DATABASE_HOST')
    DATABASE_NAME = os.getenv('DATABASE_NAME')
    DATABASE_USERNAME = os.getenv('DATABASE_USERNAME')
    DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', "")
    JWT_KEY = os.getenv('JWT_SECRET_KEY')

    # MongoDB-specific
    MONGODB_URI = os.getenv('MONGODB_URI')
    MONGODB_DATABASE = os.getenv('MONGODB_DATABASE')
    MONGODB_NOTE_COLLECTION = os.getenv('MONGODB_NOTE_COLLECTION')

    # Email configuration
    SMTP_SERVER = os.getenv('SMTP_SERVER')
    SMTP_PORT = int(os.getenv('SMTP_PORT'))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    SMTP_USE_TLS = os.getenv('SMTP_USE_TLS', 'True').lower() in ('true', '1', 'yes')
    
    # Security settings
    SESSION_COOKIE_SECURE = os.getenv('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required = [
            'SECRET_KEY', 'DATABASE_HOST', 'DATABASE_NAME', 
            'DATABASE_USERNAME'
        ]
        missing = [key for key in required if not getattr(cls, key)]
        if missing:
            raise ValueError(f"Missing required config: {missing}")
        
    GETTING_STARTED = {
  "time": 1748812919542,
  "blocks": [
    {
        "id": "pAYurTAF89",
      "type": "image",
      "data": {
        "url": "http://localhost:5000/static/logo.png",
      }
    },
    {
      "id": "pAYurTAF80",
      "type": "header",
      "data": {
        "text": "Overview",
        "level": 2
      }
    },
    {
      "id": "BV9lbJvJhF",
      "type": "paragraph",
      "data": {
        "text": "Notes.io is a modern open-source web-based note-taking platform inspired by Notion. It offers users a clean, minimal interface to create, organize, and manage their notes with rich content editing features. Built with a full-stack architecture to deliver a seamless and responsive experience.",
        "alignment": "left"
      }
    },
    {
      "id": "PyppWbVwvU",
      "type": "delimiter",
      "data": {
        "style": "line",
        "lineWidth": 100,
        "lineThickness": 3
      }
    },
    {
      "id": "cSc55OXkN3",
      "type": "header",
      "data": {
        "text": "Features",
        "level": 2
      }
    },
    {
      "id": "bKf4xzU_vc",
      "type": "list",
      "data": {
        "style": "unordered",
        "meta": {},
        "items": [
          {
            "content": "Block-based editor using <b>Editor.js</b> and <b>custom plugins</b> created by our team.",
            "meta": {},
            "items": []
          },
          {
            "content": "Real-time <b>auto-saving</b> mechanism.",
            "meta": {},
            "items": []
          },
          {
            "content": "Image attachments through a URL or local image upload.",
            "meta": {},
            "items": []
          },
          {
            "content": "Account management with <b>multi-factor</b> authentication (MFA).",
            "meta": {},
            "items": []
          },
          {
            "content": "Export notes to <b>HTML, PDF </b>and <b>MD</b> format.",
            "meta": {},
            "items": []
          },
          {
            "content": "User preferences management via settings dashboard.",
            "meta": {},
            "items": []
          },
          {
            "content": "Built to be <b>customizable </b>for your business needs.",
            "meta": {},
            "items": []
          },
          {
            "content": "Support for <b>Mermaid </b>plugin to create <b>diagrams and flowcharts</b> within notes.",
            "meta": {},
            "items": []
          },
          {
            "content": "Link preview to display <b>rich of pasted URLs</b>.",
            "meta": {},
            "items": []
          },
          {
            "content": "Tables plugin to <b>create structured tabular data blocks</b> within notes.",
            "meta": {},
            "items": []
          },
          {
            "content": "Toggle sections to <b>collapse and expand blocks</b> for better note organization.",
            "meta": {},
            "items": []
          },
          {
            "content": "Inject <b>Hyperlinks </b>through text.",
            "meta": {},
            "items": []
          },
          {
            "content": "You can simply press<b> Ctrl + Z</b> to <b>undo</b> any unintended changes.",
            "meta": {},
            "items": []
          }
        ]
      }
    },
    {
      "id": "93Rhj8p0zZ",
      "type": "delimiter",
      "data": {
        "style": "line",
        "lineWidth": 100,
        "lineThickness": 3
      }
    },
    {
      "id": "B9sjw65QF4",
      "type": "header",
      "data": {
        "text": "Suggested Use Cases",
        "level": 2
      }
    },
    {
      "id": "8LcSkvXmPg",
      "type": "list",
      "data": {
        "style": "unordered",
        "meta": {},
        "items": [
          {
            "content": "Students organizing class notes.",
            "meta": {},
            "items": []
          },
          {
            "content": "Developers documenting projects.",
            "meta": {},
            "items": []
          },
          {
            "content": "Team leaders share the tasks to be done with their team members.",
            "meta": {},
            "items": []
          },
          {
            "content": "<b>And many more...</b>",
            "meta": {},
            "items": []
          }
        ]
      }
    }
  ],
  "version": "2.31.0-rc.7"
}

 