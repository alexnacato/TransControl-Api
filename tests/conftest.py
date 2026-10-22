import os
import tempfile
from pathlib import Path

_TEST_DB_DIR = tempfile.TemporaryDirectory(prefix="transcontrol-tests-")
_TEST_DB_PATH = Path(_TEST_DB_DIR.name, "test.sqlite3")

# Debe establecerse ANTES de importar main, database o cualquier router,
# para no tocar la base configurada en .env.
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB_PATH.as_posix()}"
os.environ["SECRET_KEY"] = "solo-para-pruebas-locales-no-reutilizar"
os.environ["SMTP_USER"] = ""
os.environ["SMTP_PASS"] = ""
