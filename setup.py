from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="simplicity-tools",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python wrapper for slc-cli and zap tools with automatic platform detection and download",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/simplicity-tools",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "simplicity-tools=simplicity_tools.cli:main",
            "slc=simplicity_tools.bin_shims:slc_cli_shim",
            "zap=simplicity_tools.bin_shims:zap_cli_shim",
        ],
    },
    include_package_data=True,
    package_data={
        "simplicity_tools": ["config/*.json", "templates/*"],
    },
) 