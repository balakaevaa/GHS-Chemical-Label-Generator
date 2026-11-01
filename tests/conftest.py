import os
import pytest
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture(scope="session")
def base_url() -> str:
    return os.getenv("BASE_URL", "https://example.com")