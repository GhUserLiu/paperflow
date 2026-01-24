"""Test CLI module"""

import asyncio
import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from arxiv_zotero.cli import main


class TestCLI:
    """Test CLI entry point"""

    def test_main_missing_credentials(self, monkeypatch, capsys):
        """Test CLI exits when credentials are missing"""
        # Remove all environment variables
        monkeypatch.delenv("ZOTERO_LIBRARY_ID", raising=False)
        monkeypatch.delenv("ZOTERO_API_KEY", raising=False)

        with pytest.raises(SystemExit) as exc_info:
            main()

        # Should exit with error code
        assert exc_info.value.code != 0

    @patch("arxiv_zotero.cli.asyncio.run")
    def test_main_with_search_mode(self, mock_run, monkeypatch):
        """Test CLI in search mode"""
        # Set required environment variables
        monkeypatch.setenv("ZOTERO_LIBRARY_ID", "test_lib")
        monkeypatch.setenv("ZOTERO_API_KEY", "test_key")
        monkeypatch.setenv("TEMP_COLLECTION_KEY", "test_collection")

        # Make asyncio.run return 0 (success)
        mock_run.return_value = 0

        # Mock command line arguments
        test_args = ["cli", "--keywords", "test", "--max-results", "5", "--no-pdf"]

        with patch.object(sys, "argv", test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()

        # Should exit successfully
        assert exc_info.value.code == 0
        assert mock_run.called

    @patch("arxiv_zotero.cli.asyncio.run")
    def test_main_auto_collection(self, mock_run, monkeypatch):
        """Test auto collection mode"""
        monkeypatch.setenv("ZOTERO_LIBRARY_ID", "test_lib")
        monkeypatch.setenv("ZOTERO_API_KEY", "test_key")
        monkeypatch.setenv("TEMP_COLLECTION_KEY", "test_collection")

        # Make asyncio.run return 0 (success)
        mock_run.return_value = 0

        test_args = ["cli", "--auto"]

        with patch.object(sys, "argv", test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()

        # Verify asyncio.run was called and exit was successful
        assert mock_run.called
        assert exc_info.value.code == 0

    def test_main_invalid_args(self, monkeypatch):
        """Test CLI with invalid arguments"""
        monkeypatch.setenv("ZOTERO_LIBRARY_ID", "test_lib")
        monkeypatch.setenv("ZOTERO_API_KEY", "test_key")
        monkeypatch.setenv("TEMP_COLLECTION_KEY", "test_collection")

        # Invalid date format
        test_args = ["cli", "--keywords", "test", "--start-date", "invalid-date"]

        with patch.object(sys, "argv", test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()

        # Should exit with error code (argparse error)
        assert exc_info.value.code != 0
