from setuptools import find_packages, setup


def load_long_description(path):
    with open(path, "r") as f:
        return f.read()


def ignore_line(line):
    line = line.strip()
    return not line or line[0] == "#"


def load_requires(path):
    with open(path, "r") as requires:
        return [line.strip() for line in requires if not ignore_line(line)]


setup(
    name="AutoPyType",
    version="0.1.0",
    description="tool for automatically generating python type hints",
    long_description=load_long_description("README.md"),
    url="https://github.com/ItayTheDar/AutoPyType.git",
    author="Itay Dar",
    author_email="itayd@post.bgu.ac.il",
    license="GNU AGPLv3",
    python_requires=">=3.9.1",
    packages=find_packages(),
    install_requires=load_requires("requirements.txt"),
    entry_points={
        "console_scripts": [
            "autopy = autopy.cli.main:autopy_cli",
        ],
    },
    include_package_data=True,
)
