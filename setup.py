import setuptools

with open("emissor/representation/README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="emissor",
    version="0.0.1",
    author="CLTL",
    author_email="piek.vossen@vu.nl",
    description="Representation of multi-modal datasets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    include="emissor/representation/README.md",
    exclude="README.md",
    url="https://github.com/cltl/EMISSOR",
    namespace_packages=['emissor', 'emissor.plugins'],
    packages=['emissor.representation'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['numpy==1.20.0',
                      'marshmallow==3.11.1',
                      'marshmallow-dataclass==8.4.1',
                      'marshmallow-enum==1.5.1',
                      'rdflib==5.0.0',
                      'rdflib-jsonld==0.5.0',
                      'simplejson==3.17.2'],
    python_requires='>=3.7',
)
