import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="s3b",
    version="1.0",
    author="Markus Bartels",
    author_email="markus.bartls@capgemini.com",
    description="S3 backup for the HPI Schul-Cloud",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hpi-schul-cloud/infra-tools/tree/master/s3-backup",
    packages=setuptools.find_packages(),
    install_requires=['pyyaml']
    scripts=['s3-backup.py'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
