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
    install_requires=['numpy~=1.20',
                      'marshmallow~=3.11',
                      'marshmallow-dataclass~=8.4',
                      'marshmallow-enum~=1.5',
                      'marshmallow-union~=0.1',
                      'rdflib~=6.0',
                      'simplejson~=3.17',
                      'typeguard~=2.13'],
    python_requires='>=3.7',
    extras_require={
        "processing": ["joblib~=1.0", "tqdm~=4.60", "scikit-learn~=0.24"]
    }
)
