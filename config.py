import os
from dotenv import load_dotenv

load_dotenv()

# App Config
APP_ENV = os.getenv("APP_ENV", "development")
APP_PORT = int(os.getenv("APP_PORT", 8000))
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")

# Redis Config
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Database Config
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/streampulse")

# Logging Config
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
