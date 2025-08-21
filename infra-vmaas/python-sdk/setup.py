#Easily download, build, install, upgrade, and uninstall Python packages
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vmaas",
    version="1.0",
    author="SRE-Team",
    author_email="devops@dbildungscloud.com",
    description="Files to run our VMaaS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/",
    packages=setuptools.find_packages(),
    install_requires=['ionoscloud'],
    scripts=['sct.py'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)