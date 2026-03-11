import shutil
import pytest

from tests.common import RUNTIME_DIR



@pytest.fixture
def runtime_dir():
    # Delete RUNTIME_DIR if exist
    if RUNTIME_DIR.exists():
        shutil.rmtree(str(RUNTIME_DIR), ignore_errors=True)

    # Run the test
    yield

    # # Delete RUNTIME_DIR
    # shutil.rmtree(str(RUNTIME_DIR), ignore_errors=True)