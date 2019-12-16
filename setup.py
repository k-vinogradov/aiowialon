import setuptools

# pylint: disable=missing-function-docstring


def get_long_description():
    with open("README.md", "r") as description:
        return description.read()


def get_requirements():
    with open("requirements.txt", "r") as requirements_file:
        return requirements_file.readlines()


setuptools.setup(
    name="aiowialon",  # Replace with your own username
    version="0.0.1b",
    author="Konstantin Vinogradov",
    author_email="mail@k-vinogradov.ru",
    description="A small example package",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    keywords="wialon",
    url="https://github.com/k-vinogradov/aiowialon",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=get_requirements(),
    entry_points={"console_scripts": ["wialon_query=aiowialon.bin.wialon_query:main"],},
)
