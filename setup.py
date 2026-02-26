from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="paperflow",
    version="2.2.0",
    author="Stepan Kropachev",
    author_email="kropachev.st@gmail.com",
    description="Intelligent paper collection tool for arXiv with Zotero integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GhUserLiu/arxiv-zotero-auto",
    project_urls={
        "Bug Reports": "https://github.com/GhUserLiu/arxiv-zotero-auto/issues",
        "Source": "https://github.com/GhUserLiu/arxiv-zotero-auto",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="arxiv, zotero, research, papers, academic, automation",
    packages=find_packages(exclude=["tests", "tests.*", "examples", "dev-tools"]),
    python_requires=">=3.7",
    install_requires=[
        "arxiv>=2.0.0",
        "pyzotero>=1.5.0",
        "requests>=2.31.0",
        "pytz>=2023.3",
        "python-dotenv>=1.0.0",
        "aiohttp>=3.9.0",
        "pyyaml>=6.0",
        "PyPDF2>=3.0.0",
        "beautifulsoup4>=4.9.0",
    ],
    entry_points={
        "console_scripts": [
            "paperflow=paperflow.cli:main",
        ],
    },
    include_package_data=True,
)
