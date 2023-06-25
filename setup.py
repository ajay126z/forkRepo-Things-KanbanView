"""
KanbanView configuration file for py2app and pipy.
"""

import os
from setuptools import setup, find_packages  # type: ignore


def package_files(directory):
    """Automatically add data resources."""
    paths = []
    # pylint: disable=unused-variable
    for path, _directories, filenames in os.walk(directory):
        for filename in filenames:
            paths.append((directory, [os.path.join(path, filename)]))
    return paths


APP = ["bin/things-app"]
APP_NAME = "KanbanView"
AUTHOR = "Alexander Willner"
AUTHOR_MAIL = "alex@willner.ws"
DESCRIPTON = "A simple read-only Kanban App for Things 3"
URL = "https://kanbanview.app"
VERSION = "3.0.0"
DATA_FILES = package_files("resources")
OPTIONS = {
    "argv_emulation": False,
    "iconfile": "resources/icon.icns",
    "plist": {
        "CFBundleName": APP_NAME,
        "CFBundleDisplayName": APP_NAME,
        "CFBundleGetInfoString": APP_NAME,
        "CFBundleIdentifier": "ws.willner.kanbanview",
        "CFBundleVersion": VERSION,
        "LSApplicationCategoryType": "public.app-category.productivity",
        "LSMinimumSystemVersion": "11",
        "NSHumanReadableCopyright": "Copyright 2023 " + AUTHOR,
    },
    "optimize": "2",
}

with open("README.md", "r", encoding="utf-8") as fh:
    LONG_DESRIPTION = fh.read()

setup(
    app=APP,
    author=AUTHOR,
    author_email=AUTHOR_MAIL,
    name="things3-api",
    description=DESCRIPTON,
    long_description=LONG_DESRIPTION,
    long_description_content_type="text/markdown",
    url=URL,
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS :: MacOS X",
        "Environment :: Console",
        "Framework :: Flask",
        "Natural Language :: English",
    ],
    python_requires=">=3.8",
    version=VERSION,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
    install_requires=["things.py>=0.0.15", "pywebview>=3.0.0"],
    entry_points={
        "console_scripts": [
            "things-cli = things3.things3_cli:main",
            "things-api = things3.things3_api:main",
            "things-kanban = things3.things3_app:main",
        ]
    },
)
