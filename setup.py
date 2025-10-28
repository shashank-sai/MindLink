#!/usr/bin/env python3
"""
Setup script for the MindLink dual-model therapy system.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="mindlink-therapy",
    version="1.0.0",
    author="AI Mental Health Research Team",
    author_email="research@mindlink.ai",
    description="A dual-model AI therapy system addressing the somatic blind spot in mental health AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mindlink-ai/mindlink",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Healthcare Industry",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Healthcare Industry :: Mental Health",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "mindlink=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=["ai", "therapy", "mental-health", "llm", "psychology", "medical-diagnosis"],
    project_urls={
        "Bug Reports": "https://github.com/mindlink-ai/mindlink/issues",
        "Documentation": "https://github.com/mindlink-ai/mindlink/blob/main/README.md",
        "Source": "https://github.com/mindlink-ai/mindlink",
    },
)