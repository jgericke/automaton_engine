from setuptools import setup

setup(
    name="automaton",
    version="1.0.0",
    python_requires="~=3.7",
    description="Simple, Event-driven Automation in Python",
    author="LSD Information Technology",
    author_email="julian@lsd.co.za",
    license="MIT",
    scripts=["bin/auto.py"],
    install_requires=["asyncio>=3.4.3", "aiohttp>=3.5.4", "biome>=0.1.3"],
    setup_requires=["pytest-runner>=4.4"],
    tests_require=["pytest>=4.4.2", "pytest-asyncio>=0.10.0"],
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
