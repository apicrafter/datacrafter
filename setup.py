# This is purely the result of trial and error.

import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

import datacrafter


class PyTest(TestCommand):
    # `$ python setup.py test' simply installs minimal requirements
    # and runs the tests with no fancy stuff like parallel execution.
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = [
            '--doctest-modules', '--verbose',
            './datacrafter', './tests'
        ]
        self.test_suite = True

    def run_tests(self):
        import pytest
        sys.exit(pytest.main(self.test_args))


tests_require = [
    # Pytest needs to come last.
    # https://bitbucket.org/pypa/setuptools/issue/196/
    'pytest',
    'mock',
]


install_requires = [
    'chardet>=3.0.4',
    'click>=8.0.3',
    'dictquery>=0.4.0',
    'jsonlines>=1.2.0',
    'openpyxl>=3.0.5',
    'orjson>=3.6.6',
    'pandas>=1.1.3',
    'pymongo>=3.11.0',
    'qddate>=0.1.1',
    'tabulate>=0.8.7',
    'validators>=0.18.1',
    'xlrd>=1.2.0',
    'apibackuper',
    'requests',
    'bs4',
    'lxml',
    'pyyaml'
]


# Conditional dependencies:

# sdist
if 'bdist_wheel' not in sys.argv:
    try:
        # noinspection PyUnresolvedReferences
        import argparse
    except ImportError:
        install_requires.append('argparse>=1.2.1')


# bdist_wheel
extras_require = {
    # https://wheel.readthedocs.io/en/latest/#defining-conditional-dependencies
    'python_version == "3.8" or python_version == "3.8"': ['argparse>=1.2.1'],
}



setup(
    name='datacrafter',
    version=datacrafter.__version__,
    description=datacrafter.__doc__.strip(),
    long_description=open('README.md', 'r', encoding='utf8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/apicrafter/datacrafter/',
    download_url='https://github.com/apicrafter/datacrafter/',
    packages=find_packages(exclude=('tests', 'tests.*')),
    include_package_data=True,
    author=datacrafter.__author__,
    author_email='ivan@begtin.tech',
    license=datacrafter.__licence__,
    entry_points={
        'console_scripts': [
            'datacrafter = datacrafter.__main__:main',
        ],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    tests_require=tests_require,
    python_requires='>=3.8',
    cmdclass={'test': PyTest},
    zip_safe=False,
    keywords='json jsonl csv bson cli dataset etl data-pipelines',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.8',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Topic :: Software Development',
        'Topic :: System :: Networking',
        'Topic :: Terminals',
        'Topic :: Text Processing',
        'Topic :: Utilities'
    ],
)
