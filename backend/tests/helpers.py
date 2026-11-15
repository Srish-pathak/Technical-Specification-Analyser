import io
import tempfile
import zipfile
from pathlib import Path

from app.core.config import Settings
from app.models.database import Database


def make_settings(**kw) -> Settings:
    return Settings(**kw)


def temp_db() -> Database:
    return Database(Path(tempfile.mkdtemp()) / "test.db")


def make_zip(entries: dict, compression=zipfile.ZIP_DEFLATED) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression) as z:
        for name, content in entries.items():
            z.writestr(name, content)
    return buf.getvalue()


SAMPLE_BAD = '''"""Sample module with known issues."""
import os
import json
import hashlib
import subprocess
import pickle

API_KEY = "sk_live_abcdef123456"


def risky(user_input, data=[]):
    eval(user_input)
    os.system("ls " + user_input)
    subprocess.run(user_input, shell=True)
    pickle.loads(data)
    hashlib.md5(b"x")
    try:
        pass
    except:
        pass


def deep(a, b, c, d, e, f):
    if a:
        for i in b:
            while c:
                if d:
                    for j in e:
                        if f:
                            pass
    return a and b or c
'''
