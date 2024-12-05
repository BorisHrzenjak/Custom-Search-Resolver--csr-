from setuptools import setup, find_packages

setup(
    name="csr",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",
        "rich>=10.0.0",
        "pathlib>=1.0.1",
    ],
    entry_points={
        "console_scripts": [
            "csr=csr.cli:main",
        ],
    },
    author="Boris H",
    description="Custom Search Resolver - search tool for Windows command line",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
)
