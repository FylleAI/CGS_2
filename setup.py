"""Setup script for CGS_2 project."""

from setuptools import setup, find_packages

setup(
    name="cgs2",
    version="1.0.0",
    packages=find_packages(include=["cards", "cards.*", "core", "core.*", "api", "api.*", "onboarding", "onboarding.*"]),
    python_requires=">=3.9",
    install_requires=[
        "pydantic>=2.0.0",
        "asyncpg>=0.29.0",
        "fastapi>=0.100.0",
    ],
)

