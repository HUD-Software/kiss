from pathlib import Path
import shutil
import pytest

RUNTIME_DIR = Path("runtime")
@pytest.fixture
def runtime_dir():
    yield
    shutil.rmtree(str(RUNTIME_DIR), ignore_errors=True)