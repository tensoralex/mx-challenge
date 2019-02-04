from setuptools import setup, find_packages
import re


def cleanup(x):
    return re.sub(r' *#.*', '', x.strip())


def to_list(buffer):
    return list(filter(None, map(cleanup, buffer.splitlines())))


requirements = to_list("""
    pyyaml
    requests
    fastavro
""")

setup_requirements = to_list("""
    pytest-runner
    setuptools>=36.2
""")

test_requirements = to_list("""
    pytest
    pylint
    pytest-asyncio
""")

setup(
    name='mx-challenge',
    version="0.0.1",

    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    setup_requires=setup_requirements,
    tests_require=test_requirements,
    python_requires='>=3.7',
    test_suite='tests',

)
