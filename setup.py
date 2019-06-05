from setuptools import setup, find_packages, Extension

setup(
    name="automaton_engine",
    version="1.0.1",
    python_requires="~=3.7",
    description="Simple, Event-driven Automation in Python using Elasticsearch data to inform automation decisions",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Julian Gericke, LSD Information Technology",
    author_email="julian@lsd.co.za",
    url="https://github.com/jgericke/automaton_engine",
    packages=find_packages(exclude=("tests", "tests.*")),
    entry_points={
        "console_scripts": ["automaton-engine = automaton_engine.runner:runner"]
    },
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Environment :: MacOS X",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Topic :: System :: Systems Administration",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Logging",
    ],
    install_requires=["asyncio>=3.4.3", "aiohttp>=3.5.4", "biome>=0.1.3"],
    setup_requires=["pytest-runner>=4.4"],
    tests_require=["pytest>=4.4.2", "pytest-asyncio>=0.10.0", "asynctest>=0.13.0"],
    extras_require={
        "dev": [
            "coverage>=4.5.3",
            "black>=19.3b0",
            "setuptools-black>=0.1.4",
            "flake8>=3.7.7",
            "pre-commit>=1.16.1",
        ]
    },
)
