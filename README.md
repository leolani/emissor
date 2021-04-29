# EMISSOR

EMISSOR is a repo to represent and annotate multimodal interaction in combination with an episodic memory for referential grounding.

EMISSOR stands for \textbf{E}pisodic \textbf{M}emories and \textbf{I}nterpretations with \textbf{S}ituated 
\textbf{S}cenario-based \textbf{O}ntological \textbf{R}eferences. 
The platform stores streams of multiple modalities as parallel signals. 
Each signal can be segmented independently and annotated with interpretation. 
However, these annotations do not stand on their own, but they are eventually mapped to explicit identities, 
relations, and properties in an episodic Knowledge Graph (eKG) for capturing instances of situations. 
We ground signal segments to formal instance representations and ground different modalities across each other 
through these representations. We represent natural conversations in situated contexts in which actions and 
utterances can be responses but can also happen independently. In addition, we capture these episodic experiences 
as an explicit cumulative interpretation of streams of signals. 

Unique to our approach is that these annotations are eventually mapped to explicit identities 
and relations in an RDF Knowledge Graph for capturing instances in situations which allows for 
different interpretations across modalities, sources and experiences. 
Likewise, we ground signal segments to unique instance representations and 
ground different modalities across each other through these representations. 
The Knowledge Graph represents a transparent episodic memory that can be used for reasoning.
EMISSOR can represent any (multimodal) interaction that takes place in either a virtual or
real-world setting involving any virtual or real-world agent. Through this representation,
we can record and annotate experiments, share data, evaluate system behavior and their performance 
for preset goals but also model the accumulation of knowledge and interpretations in the Knowledge Graph 
as a result of these episodic experiences. 

Although EMISSOR can be connected to any kind of eKG to model situations, 
this release includes an episodic memory that supports reasoning over conflicting information and 
uncertainties that may result from multimodal experiences.

## [Data Representation](gmrc/representation/README.md)

This repository provides the [`gmrc.representation`](gmrc/representation/README.md) Python package with data classes for
the representation of multi-modal interaction. A detailed description of the representation model can be found in the
[README](gmrc/representation/README.md) of this package. For usage outside of this repository a distribution of the
package can be built from the `setup.py` by executing

    > python setup.py sdist

## [Annotation Tool](gmrc/annotation/README.md)

In addition to the `gmrc.representation` package, this repo provides a tool that allows you to load multi-modal interaction
data with annotations and to manually edit the data by grounding it to the 
temporal and spatial containers ads well as by adding any annotations. For a
detailed description see the [README](gmrc/annotation/README.md) of the annotation
tool.

## Example data

Example data can be found in [*example_data/*](example_data) directory. Some of them are annotated by human and some are by machine. You can visualize them with the annotation tool. We highly recommend this, since it gives you how the modalities are referenced / grounded with each other.


## [How to create GMRC annotations from existing datasets](https://github.com/tae898/multimodal-datasets)

This repo collects multimodal datasets, process them, and annotate them in the GMRC annotation format. 

This is done by [Taewoon Kim](https://tae898.github.io/). Ask him if you have any questions.

## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See [`LICENSE`](https://github.com/leolani/cltl-combot/blob/main/LICENCE) for more information.

## Authors
* [Piek Vossen](https://github.com/piekvossen)
* [Thomas Baier](https://github.com/numblr)
* [Taewoon Kim](https://tae898.github.io/)
* [Selene Báez Santamaría](https://selbaez.github.io/)
* [Lea Krause](https://github.com/orgs/cltl/people/lkra)
* [Jaap Kruijt]()
