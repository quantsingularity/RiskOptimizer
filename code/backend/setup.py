"""
Setup script for RiskOptimizer Backend
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# Read version
def read_version():
    version_file = os.path.join(os.path.dirname(__file__), "__init__.py")
    with open(version_file, "r", encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    return "0.1.0"

setup(
    name="riskoptimizer-backend",
    version=read_version(),
    author="RiskOptimizer Team",
    author_email="team@riskoptimizer.com",
    description="Advanced Financial Risk Management and Portfolio Optimization System",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/abrar2030/RiskOptimizer",
    project_urls={
        "Bug Tracker": "https://github.com/abrar2030/RiskOptimizer/issues",
        "Documentation": "https://docs.riskoptimizer.com",
        "Source Code": "https://github.com/abrar2030/RiskOptimizer",
    },
    packages=find_packages(exclude=["tests*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Framework :: FastAPI",
    ],
    python_requires=">=3.11",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "httpx>=0.24.0",
            "factory-boy>=3.2.0",
        ],
        "docs": [
            "mkdocs>=1.5.0",
            "mkdocs-material>=9.0.0",
            "mkdocstrings[python]>=0.22.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "riskoptimizer-server=app:main",
            "riskoptimizer-worker=tasks.celery_app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml", "*.json"],
    },
    zip_safe=False,
    keywords=[
        "finance",
        "risk-management", 
        "portfolio-optimization",
        "monte-carlo",
        "var",
        "cvar",
        "fastapi",
        "celery",
        "quantitative-finance"
    ],
)

