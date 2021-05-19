# EMISSOR


EMISSOR stands for **E**pisodic **M**emories and **I**nterpretations with **S**ituated 
**S**cenario-based **O**ntological **R**eferences. 

EMISSOR is a platform to represent and annotate multimodal interaction 
in combination with an episodic memory for referential grounding and cumulative knowledge
growth from interactions.

The platform stores streams of multiple modalities as parallel signals.
Each signal can be segmented independently and annotated with interpretations. 
However, these annotations do not stand on their own, but they are eventually mapped to explicit identities,
relations, and properties in an episodic Knowledge Graph (**eKG**) for capturing instances of situations. 
Our model grounds signal segments to formal instance representations and it grounds different modalities (e.g. vision and references in dialogues) across each other 
through these representations. EMISSOR captures natural conversations in situated contexts in which actions and 
utterances can be responses to each other in situations but can also happen independently. We achieve this through
a flexible and robust data architecture with separate independent storage of data in different modalities
that can be aligned through so-called temporal and spatial containers. Through this representation, we can record and annotate experiments, share data, evaluate system behavior and their performance 
for preset goals but also model the accumulation of knowledge and interpretations in the **eKG**
as a result of these episodic experiences.

Although EMISSOR can be connected to any kind of eKG to model situations, this release 
includes an episodic memory that supports reasoning over conflicting information and 
uncertainties that may result from multimodal experiences. Our model allows for 
different interpretations across modalities, sources and experiences. Finally note that EMISSOR can also be used
without any eKG to represent and annotate multimodal interaction data.

## [Data Representation](emissor/representation/README.md)

This repository provides the [`emissor.representation`](emissor/representation/README.md) Python package with data classes for
the representation of multi-modal interaction. A detailed description of the representation model can be found in the
[README](emissor/representation/README.md) of this package. For usage outside of this repository a distribution of the
package can be built from the `setup.py` by executing

    > python setup.py sdist

## [Annotation Tool](emissor/annotation/README.md)

In addition to the `emissor.representation` package, this repo provides a tool that allows you to load multi-modal interaction
data with annotations and to manually edit the data by grounding it to the
temporal and spatial containers ads well as by adding any annotations. For a
detailed description see the [README](emissor/annotation/README.md) of the annotation
tool.

## Example data

Example data can be found in [*example_data/*](example_data) directory. Some of them are annotated by human and some are by machine. You can visualize them with the annotation tool. We highly recommend this, since it gives you how the modalities are referenced / grounded with each other.


## [How to create EMISSOR annotations from existing datasets](https://github.com/tae898/multimodal-datasets)

This repo collects multimodal datasets, process them, and annotate them in the EMISSOR annotation format.

This is done by [Taewoon Kim](https://taewoonkim.com/). Ask him if you have any questions.

## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

##  Citation

Please cite the following paper if you use EMISSOR in your research:

{inproceedings@{emissor:2021,
        title = {EMISSOR: A platform for capturing multimodal interactions as Episodic Memories and Interpretations with Situated Scenario-based Ontological References},
        author = {Selene Baez Santamaria and Thomas Baier and Taewoon Kim and Lea Krause and Jaap Kruijt and Piek Vossen},
        url={https://mmsr-workshop.github.io/programme},
        booktitle = {Processings of the MMSR workshop "Beyond Language: Multimodal Semantic Representations", IWSC2021},
        year = {2021}
}

## License

Distributed under the MIT License. See [`LICENSE`](https://github.com/cltl/EMISSOR/blob/main/LICENCE) for more information.

## Authors
* [Piek Vossen](https://github.com/piekvossen)
* [Thomas Baier](https://github.com/numblr)
* [Taewoon Kim](https://taewoonkim.com)
* [Selene Báez Santamaría](https://selbaez.github.io/)
* [Lea Krause](https://github.com/orgs/cltl/people/lkra)
* [Jaap Kruijt]()
