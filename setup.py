import setuptools

with open("VERSION", "r") as fh:
    version = fh.read().strip()

with open("emissor/representation/README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="emissor",
    version=version,
    author="CLTL",
    author_email="piek.vossen@vu.nl",
    description="Representation of multi-modal datasets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    include="emissor/representation/README.md",
    exclude="README.md",
    url="https://github.com/cltl/EMISSOR",
    data_files=[('VERSION', ['VERSION'])],
    namespace_packages=['emissor'],
    packages=['emissor.representation', 'emissor.processing', 'emissor.persistence'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['numpy',
                      'marshmallow',
                      'marshmallow-dataclass',
                      'marshmallow-enum',
                      'marshmallow-union',
                      'rdflib',
                      'simplejson',
                      'typeguard'],
    python_requires='>=3.7',
    extras_require={
        "processing": ["joblib", "tqdm", "scikit-learn"]
    }
)
