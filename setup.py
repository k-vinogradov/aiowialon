import setuptools

# pylint: disable=missing-function-docstring


def get_long_description():
    with open("README.md", "r") as description:
        return description.read()


setuptools.setup(
    name="aiowialon",  # Replace with your own username
    version="0.0.1",
    author="Konstantin Vinogradov",
    author_email="mail@k-vinogradov.ru",
    description="A small example package",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/k-vinogradov/aiowialon",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL-3.0 License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
