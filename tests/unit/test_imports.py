"""Test basic imports"""


def test_imports():
    """Test that main components can be imported"""
    try:
        from arxiv_zotero import (
            ArxivSearchParams,
            ArxivZoteroCollector,
            PaperSummarizer,
            PDFManager,
            load_credentials,
        )

        assert True
    except ImportError as e:
        assert False, f"Import failed: {e}"


def test_search_params():
    """Test ArxivSearchParams creation"""
    from arxiv_zotero import ArxivSearchParams

    params = ArxivSearchParams(keywords=["test"], max_results=5)
    assert params.keywords == ["test"]
    assert params.max_results == 5
