from functools import lru_cache

from app.core.config import get_settings
from app.models.database import Database


@lru_cache(maxsize=1)
def get_db() -> Database:
    return Database(get_settings().db_path)
