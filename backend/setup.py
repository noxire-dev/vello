"""
Setup configuration for Vello package.
"""
from setuptools import find_packages, setup

setup(
    name="vello",
    version="0.1.0",
    description="Automation-First Email Outreach System",
    author="NovaLare",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "sqlalchemy",
        "python-dotenv",
        "jinja2",
    ],
)
