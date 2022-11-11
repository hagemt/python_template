"""setup.py is only necessary if pyproject.toml can't specify install options!

(it does provide a traditional entry point for `pip install -e .` in dev/test)
"""
from setuptools import find_packages, setup

_AUTHORS = "Tor E Hagemann"
_CONTACT = "hagemt@users.noreply.github.com"
_GIT_URL = "github.com/hagemt/python-template"
_LICENSE = "MIT"


def read_utf8(filename: str, encoding="UTF-8") -> list:
    with open(filename, encoding=encoding) as file:
        return file.readlines()


def read_deps(filename: str, comment="#") -> list:
    deps = []
    for line in read_utf8(filename):
        stripped = line.strip()
        if stripped and not line.startswith(comment):
            deps.append(stripped)
    return deps


markdown = read_utf8("README.md")
_PY_NAME = str(markdown[0])[1:].strip()
_VERSION = "".join(read_utf8("VERSION.txt")).strip()

tools = read_deps("requirements-testing.txt")
basic = read_deps("requirements.txt")

about = markdown[2].strip()


setup(
    # basics:
    name=_PY_NAME,
    version=_VERSION,
    # keep these sorted:
    author=_AUTHORS,
    author_email=_CONTACT,
    description=about,
    license=_LICENSE,
    long_description="".join(markdown),
    packages=find_packages(include=[_PY_NAME, _PY_NAME + ".*"], where="src"),
    package_dir={"": "src"},  # src-layout project style, no tests in dist
    url=_GIT_URL,
    # reverse sorted:
    tests_require=tools,
    python_requires=">=3.8,<4",
    install_requires=basic,
    extras_require={
        "testing": tools,
    },
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
    ],
)
