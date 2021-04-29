# convert2emissor

**This has been moved to https://github.com/tae898/multimodal-datasets.**

<s>This directory includes a shell script to download the datasets and a python script to annotate them in the EMISSOR format.

Below is an example of loading the EMISSOR annotated MELD dataset with the webapp GUI.

![convert2emissor example](convert2emissor.png)

## Things to note

- The unit of the unix time stamps is milliseconds.
- Probably this is not perfect (work in progress).

## Requirements

Install the requriements by

```
pip install -r requirements.txt
```
I highly recommend you to run above command in your virtual python environment.

## Instructions

### 1. Download the datasets

In the current directory where this `README.md` is located, run
```
bash download.sh IEMOCAP MELD
```

### 2. Annotate the datasets in the EMISSOR format

In the current directory where this `README.md` is located, run
```
python3 run.py --num-jobs=16
```
Change the value 16 to whatever you want, depending on the number of CPU cores your machine has.

## TODOs

1. Add audio when the webapp supports audio playback option.
1. Add video when the webapp supports video playback option. Currently the webapp only supports images, and thus the frames are sampled by a fixed interval from the original video clips.
1. Add a feature where a user can annotate a face. Although face-recognition is done, the machine does not know the real name of faces. So the machine gives them random names (e.g. adorable-jaybird). A simple clustering is done to group similar faces.
1. Add a feature where the name of a speaker is visible in the text section.
1. Add a feature where the emotion of the person is linked to the face / speaker.


## Authors

- Taewoon Kim (t.kim@vu.nl)

</s>
