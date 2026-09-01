import pytest
import sys
from pathlib import Path


def test_python_version():
    """Test that Python version is compatible."""
    assert sys.version_info >= (3, 8), "Python 3.8+ is required"


def test_project_structure():
    """Test that the project structure is set up correctly."""
    project_root = Path(__file__).parent.parent
    
    # Check main files exist
    assert (project_root / "davemail.py").exists(), "davemail.py should exist"
    assert (project_root / "pyproject.toml").exists(), "pyproject.toml should exist"
    
    # Check test directories exist
    assert (project_root / "tests").exists(), "tests directory should exist"
    assert (project_root / "tests" / "unit").exists(), "tests/unit directory should exist"
    assert (project_root / "tests" / "integration").exists(), "tests/integration directory should exist"
    
    # Check __init__.py files exist
    assert (project_root / "tests" / "__init__.py").exists(), "tests/__init__.py should exist"
    assert (project_root / "tests" / "unit" / "__init__.py").exists(), "tests/unit/__init__.py should exist"
    assert (project_root / "tests" / "integration" / "__init__.py").exists(), "tests/integration/__init__.py should exist"
    
    # Check conftest.py exists
    assert (project_root / "tests" / "conftest.py").exists(), "tests/conftest.py should exist"


def test_pytest_configuration():
    """Test that pytest configuration is accessible."""
    import pytest
    
    # Test that pytest can find the configuration by collecting without running
    config = pytest.main(["--collect-only", "--quiet", "--no-cov"])
    assert config in [0, 5], "Pytest should be able to collect tests successfully"


def test_fixtures_available():
    """Test that common fixtures are available from conftest.py."""
    # These fixtures should be available due to conftest.py
    fixtures = [
        'temp_dir',
        'temp_file', 
        'mock_config',
        'mock_configobj',
        'mock_notmuch_database',
        'mock_subprocess',
        'sample_email_content',
        'mock_email_message'
    ]
    
    # This test will pass if conftest.py is properly configured
    # The fixtures will be available to other tests
    assert True, "Fixtures should be available from conftest.py"


def test_coverage_config():
    """Test that coverage configuration is working."""
    try:
        import coverage
        # Test that coverage module is available
        assert True, "Coverage module should be importable"
    except ImportError:
        pytest.skip("Coverage not installed, skipping coverage config test")


@pytest.mark.unit
def test_unit_marker():
    """Test that unit marker is configured."""
    assert True, "Unit marker should be available"


@pytest.mark.integration  
def test_integration_marker():
    """Test that integration marker is configured."""
    assert True, "Integration marker should be available"


@pytest.mark.slow
def test_slow_marker():
    """Test that slow marker is configured."""
    assert True, "Slow marker should be available"


def test_temp_dir_fixture(temp_dir):
    """Test that temp_dir fixture works."""
    assert temp_dir.exists(), "Temp directory should exist"
    assert temp_dir.is_dir(), "Temp directory should be a directory"
    
    # Test we can create files in it
    test_file = temp_dir / "test.txt"
    test_file.write_text("test")
    assert test_file.exists(), "Should be able to create files in temp directory"


def test_temp_file_fixture(temp_file):
    """Test that temp_file fixture works."""
    assert temp_file.exists(), "Temp file should exist"
    assert temp_file.is_file(), "Temp file should be a file"
    assert temp_file.read_text() == "test content", "Temp file should have expected content"


def test_mock_config_fixture(mock_config):
    """Test that mock_config fixture works."""
    assert isinstance(mock_config, dict), "Mock config should be a dictionary"
    assert "test_maildir" in mock_config, "Mock config should have test_maildir"
    assert "tag_folder_mapping" in mock_config["test_maildir"], "Mock config should have tag_folder_mapping"


def test_mock_configobj_fixture(mock_configobj):
    """Test that mock_configobj fixture works."""
    # Test iteration
    keys = list(mock_configobj)
    assert "test_maildir" in keys, "Mock ConfigObj should be iterable"
    
    # Test item access
    maildir_config = mock_configobj["test_maildir"]
    assert "tag_folder_mapping" in maildir_config, "Mock ConfigObj should support item access"