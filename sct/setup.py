import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sct",
    version="1.0",
    author="Lars Dahlke",
    author_email="lars.dahlke@capgemini.com",
    description="Dynamic tunnel to access IONOS Kubernets Cluster via jump host",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hpi-schul-cloud/infra-tools/tree/master/sct",
    packages=setuptools.find_packages(),
    install_requires=['sshtunnel', 'pyyaml', 'ionoscloud'],
    scripts=['sct.py'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
