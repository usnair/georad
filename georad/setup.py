import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="usnair", # Replace with your own username
    version="0.0.1",
    author="Udaysankar Nair of UAH, Huntsville, Alabama",
    author_email="example_email@example.com",
    description="This package provides a dashboard for utilizing cloud based atmospheric science data sets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/usnair/georad",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
