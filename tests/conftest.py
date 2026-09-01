import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_file(temp_dir):
    """Create a temporary file for testing."""
    temp_file = temp_dir / "test_file.txt"
    temp_file.write_text("test content")
    return temp_file


@pytest.fixture
def mock_config():
    """Mock configuration object for testing."""
    return {
        "test_maildir": {
            "tag_folder_mapping": {
                "inbox": "INBOX",
                "sent": "Sent",
                "new": "new"
            }
        }
    }


@pytest.fixture
def mock_configobj(mock_config):
    """Mock ConfigObj instance."""
    mock = MagicMock()
    mock.__iter__ = lambda self: iter(mock_config.keys())
    mock.__getitem__ = lambda self, key: mock_config[key]
    return mock


@pytest.fixture
def mock_notmuch_database():
    """Mock notmuch database for testing."""
    mock_db = MagicMock()
    mock_query = MagicMock()
    mock_message = MagicMock()
    
    mock_message.get_filename.return_value = "/path/to/message"
    mock_message.get_tags.return_value = ["inbox", "unread"]
    mock_message.add_tag.return_value = None
    mock_message.remove_tag.return_value = None
    
    mock_query.search_messages.return_value = [mock_message]
    mock_db.create_query.return_value = mock_query
    mock_db.__enter__ = lambda self: mock_db
    mock_db.__exit__ = lambda self, *args: None
    
    return mock_db


@pytest.fixture
def mock_subprocess():
    """Mock subprocess calls for testing."""
    mock = MagicMock()
    mock.call.return_value = 0
    mock.check_output.return_value = b"test output"
    return mock


@pytest.fixture(autouse=True)
def clean_environment():
    """Clean environment variables before each test."""
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def sample_email_content():
    """Sample email content for testing."""
    return """From: test@example.com
To: recipient@example.com
Subject: Test Email
Date: Mon, 01 Jan 2024 12:00:00 +0000

This is a test email content.
"""


@pytest.fixture
def mock_email_message():
    """Mock email.message.Message object."""
    mock = MagicMock()
    mock.get.return_value = "test@example.com"
    mock.get_all.return_value = ["test@example.com"]
    mock.get_content_type.return_value = "text/plain"
    mock.get_payload.return_value = "test email body"
    return mock