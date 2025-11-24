"""
SysPulse Setup Script

For packaging and distribution
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="syspulse",
    version="1.0.0",
    author="SysPulse Team",
    description="System utilities dashboard that translates technical controls into human language",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/batkins33/BA_Sandbox",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=[
        "psutil>=5.9.0",
        "pyyaml>=6.0",
        "requests>=2.31.0",
        "tabulate>=0.9.0",
        "colorama>=0.4.6",
    ],
    entry_points={
        "console_scripts": [
            "syspulse=syspulse:main",
        ],
    },
    include_package_data=True,
)
