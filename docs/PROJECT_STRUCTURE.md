# Project Structure

## 📁 Directory Organization

```
arxiv-zotero-connector/
├── .github/
│   └── workflows/              # GitHub Actions CI/CD workflows
│       └── daily-paper-collection.yml
│
├── arxiv_zotero/               # Main package source code
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py                  # Command-line interface
│   │
│   ├── clients/                # API clients
│   │   ├── __init__.py
│   │   ├── arxiv_client.py     # arXiv API client
│   │   └── zotero_client.py    # Zotero API client
│   │
│   ├── config/                 # Configuration modules
│   │   ├── __init__.py
│   │   ├── arxiv_config.py     # arXiv to Zotero field mapping
│   │   └── metadata_config.py  # Metadata transformation logic
│   │
│   ├── core/                   # Core business logic
│   │   ├── __init__.py
│   │   ├── connector.py        # Main connector class
│   │   ├── paper_processor.py  # Paper processing with duplicate detection
│   │   └── search_params.py    # Search parameter models
│   │
│   └── utils/                  # Utility modules
│       ├── credentials.py      # Credential management
│       ├── pdf_manager.py      # PDF download and handling
│       └── summarizer.py       # AI-powered summarization
│
├── config/                     # Configuration files
│   └── .env.example            # Environment variables template
│
├── docs/                       # Documentation
│   ├── api-docs.md             # API documentation
│   ├── PROJECT_FEATURES.md     # Feature documentation
│   └── TEST_REPORT.md          # Test reports
│
├── examples/                   # Example usage
│   └── my_search_example.yaml  # Search configuration example
│
├── logs/                       # Log files (gitignored)
│   ├── .gitkeep                # Keep directory in git
│   └── arxiv_zotero.log        # Application log
│
├── output/                     # Output files (gitignored)
│   └── .gitkeep                # Keep directory in git
│
├── scripts/                    # Executable scripts
│   └── auto_collect.py         # Main collection script
│
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── test_imports.py         # Import tests
│   └── test_duplicate_detection.py  # Duplicate detection tests
│
├── .env                        # Environment variables (local, gitignored)
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── LICENSE                     # MIT License
├── MANIFEST.in                 # Package manifest
├── PROJECT_STRUCTURE.md        # This file
├── README.md                   # Main documentation
├── pyproject.toml              # Python project configuration
├── requirements.txt            # Python dependencies
└── setup.py                    # Package setup script
```

## 📂 Directory Purposes

### `/arxiv_zotero` - Main Package
Contains all the Python source code for the arxiv-zotero-connector package.

### `/config` - Configuration Files
Stores configuration templates and example files. The actual `.env` file should be in the root directory.

### `/docs` - Documentation
Contains all project documentation including API docs, feature descriptions, and test reports.

### `/examples` - Example Usage
Provides example configurations and usage patterns.

### `/logs` - Log Files
Stores application logs. The directory is tracked by git, but log files are ignored.

### `/output` - Output Files
Temporary output directory for downloaded files and generated content.

### `/scripts` - Executable Scripts
Contains standalone scripts that can be run directly.

### `/tests` - Test Suite
All unit tests and integration tests.

## 🔧 File Naming Conventions

- **Python modules**: `snake_case.py`
- **Configuration files**: `snake_case.yaml`, `.env`
- **Documentation**: `descriptive-name.md`
- **Logs**: `arxiv_zotero.log`

## 🚀 Quick Start

### Running the Main Script
```bash
python scripts/auto_collect.py
```

### Running Tests
```bash
python -m pytest tests/
```

### Viewing Logs
```bash
cat logs/arxiv_zotero.log
```

## 📝 Notes

- The `.env` file should never be committed to git
- Log files in `/logs` are gitignored
- The `/output` directory is for temporary files only
- Configuration examples are in `/config` directory
- All documentation is centralized in `/docs`

---

**Last Updated**: 2025-12-25
