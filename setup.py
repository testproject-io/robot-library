import setuptools

from TestProjectLibrary import definitions

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="testproject-robot-library",
    version=definitions.get_lib_version(),
    author="TestProject",
    author_email="contact@testproject.io",
    description="TestProject.io Library for the Robot Framrwork",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://testproject.io/selenium-appium-powered-sdk/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "robotframework-seleniumlibrary>=4.5.0",
        "testproject-python-sdk>=0.63.19",
        "importlib-metadata>=1.7.0",
        "packaging>=20.4",
    ],
)
