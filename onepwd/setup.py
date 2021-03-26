import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="onepwd",
    version="1.0.1",
    author="HPI Schulcloud",
    author_email="devops@hpi-schul-cloud.de",
    description="Utilities to work with 1password",
    long_description=long_description,
    url="https://github.com/hpi-schul-cloud/infra-tools",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    scripts=['bin/onepwd'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU AFFERO GENERAL PUBLIC LICENSE V3",
        "Operating System :: OS Independent",
    ],
)