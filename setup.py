import setuptools

with open("gmrc/representation/README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gmrc",
    version="0.0.1-dev",
    author="CLTL",
    author_email="piek.vossen@vu.nl",
    description="Representation of multi-modal datasets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    include="gmrc/representation/README.md",
    exclude="README.md",
    url="https://github.com/cltl/GMRCAnnotation",
    packages=['gmrc.representation'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)