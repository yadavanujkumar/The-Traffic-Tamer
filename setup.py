"""
Setup script for Traffic Tamer
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="traffic-tamer",
    version="1.0.0",
    author="Yadav Anuj Kumar",
    description="Multi-Agent Traffic Simulation Platform with Game Theory and Reinforcement Learning",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yadavanujkumar/The-Traffic-Tamer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Mathematics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "traffic-tamer=main:main",
        ],
    },
    keywords="traffic simulation game-theory reinforcement-learning multi-agent marl",
    project_urls={
        "Bug Reports": "https://github.com/yadavanujkumar/The-Traffic-Tamer/issues",
        "Source": "https://github.com/yadavanujkumar/The-Traffic-Tamer",
    },
)
