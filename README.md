# GMRC Annotations

This repo provides a tool for the annotation of multimodal interaction, following the GMRC (Goal-oriented Multimodal Robot Collaboration) framework.
GMRC is an easy-to-use representation for storing and exchanging recordings and annotations of multimodal interaction data.

The goal of GMRC is to exchange these interactions, where contributors are free to generate interactions in any way they like but need to represent
the starting conditions, the goals and the recoding of the interaction in a uniform way. The interactions are represented in different modalities: 
video, image, audio, text, while the data units are aligned in so-called temporal and spatial containers. 

More information on GMRC and the format will be provided here: [LINK TO BE PROVIDED]

The tool that is described in this repo allows you to load such data with annotations and to manually edit the data by grounding it to the 
temporal and spatial containers ads well as by adding any annotations.

## Install

* Run the frontend, either from a docker container 

        > docker run --rm -ti -v /absolute/path/to/repository/GMRCAnnotation/webapp:/app trion/ng-cli npm install
        > docker run --rm -ti -p 4200:4200 -v /absolute/path/to/repository/GMRCAnnotation/webapp:/app trion/ng-cli ng serve --host 0.0.0.0

  or by install node.js and angular

        > brew install angular-cli
        > ng --version
        > cd webapp
        >
        > ng serve

  If you run into issues with node versions, try in *webapp/*:
  
        > npm i -g npm-check-updates
        > ncu -u
        > npm install
        
* Setup certificate next to `app.py` 

        > openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
        
* Setup python

        > python -m venv venv
        > source venv/bin/activate
        > pip install -r requirements.txt

* Run the webserver, optionally with the **absolute path** to the folder containing the scenario data. If no data folder
is specified, *data/* is used by default.
It is recommended to choose a separate data folder, then you can easily use version control on the data folder (see below). 

        > python app.py -d /absolute/path/to/my/scenarios
        
  **When starting the webserver for the first time, visit `https://localhost:5000/api/scenario` in the browser and accept
  the certificate.** Otherwise the browser will not be able to load data from the backend.
  
* Open the GUI at `https://localhost:4200` in your browser.
  
# Add data

By default the *data/* folder in this repository is used, any other folder can be specified when running `app.py`.
Expected folder structure:

        |- data/
          |- scenario_name_1/
            |- image
              |- pic_1603139010.jpg
            |- text
              |- chat_1.csv
            image.json
            scenario_name_1.json
            text.json
          |- scenario_name_2/
            |- image
            |- text
            image.json
            scenario_name_2.json
            text.json

The tool helps to edit the json files with the scenario metadata in the above tree structure.
If the files already exist, they are used, if not, the will be generated from the content of the 
`image/` and `text/` folders in each scenario. 

The *.csv* files for the text signals are currently expected to contain at least an `utterance` and `time` column.

**Note that the tool will create one signal for each
image entry, i.e. if an image should be present multiple times, multiple copies of it should be placed in the image folder.**

### Preprocessing

When the metadata is not present and is created by this tool, it will infer some information about the data and create
some default annotations:

#### Timing
The tool will try to guess the timestamps of the signals. For text it will
be loaded from the *.csv* file, for images it will try to infer it from the file name. For inference of the timestamp it
assumes that the are in seconds between 1970 and 2070. If no timestamps are present for images, they will be placed 
at the start of the scenario.


#### Tokenization

The tool will perform tokenization of the text signals in the provided *.csv* files and add the tokens as annotations
to the text signals.

#### Display values

The will add annotations containing display values that can are used in the GUI to show labels for segments and mentions.

## Usage

![Screenshot Image](doc/img/screenshot_image.png)

### Workflow for images

1. Select a scenario
1. Select a modality
1. Show a list of the signals for the scenario (folded by default)
1. Select a signal either from the list of signals or from the timeline
1. Click the Badge of the signal in the list to enable positioning on the timeline and move the slider. When done
   click the Badge again to disable time editing. *Note: currently the selection get's lost when disabling editing* 
1. Select a segment from the list of segments. When selected dragging the bounding box can be enabled by clicking
   on the label below the bounding box. Size can be adjusted by dragging the bottom right corner of the bounding box. 
1. Expand the segment for editing (same for annotations)
1. Add a mention (generatates a single bounding box for the image)
1. Add annotations to the mention after selecting an annotation type.
1. **Save after modifications (you can use any of the *Save* buttons, they all save the whole scenario)**

### Workflow for text

![Screenshot Text](doc/img/screenshot_text.png)

For step 1. - 5. follow the instructions for images.
1. Add a mention (empty by default)
1. Select the tokens that belong to the mention by clicking on them.
1. Select a mention by selecting a segment from the segment list (to be improved) or an annotation from the
   annotation list
1. Expand segment or annotation for editing (to be improved).
1. Add annotations to the mention after selecting an annotation type.
1. **Save after modifications (you can use any of the *Save* buttons, they all save the whole scenario)**

### Version Control

Save as often as possible! Setup version control (git) in your data folder and use it to track your changes to the JSON
files to version control, as currently there is no *Undo* functionality! If you don't want to include the data files,
add the following *.gitignore* to the data folder:

        # Ignore everything except JSON files
        *
        !*.json
        
**Note that for the default folder `data` in this repository the content is ignored, it is prefered to use a folder outside
of this repository and setup a separate git repository only for the data.**

## Issues

#### Caching

Sometimes there can be issues with caching in the browser, especially if changes are pulled from GitHub,
if you run into strange behaviour try to clear the cache in your Browser (only Cache is enough, cookies etc. is not necessary)

#### Switching between scenarios

Switching between scenarios does not work, reload the page instead before choosing the scenario.

#### Editing Scenario meta data

This is not supported yet, edit the JSON file directly. It is also not possible to edit the time range of the scenario,
a workaround is to generate the JSON files when the data is loaded the first time, then edit the scenario JSON, remove
image.json and text.json and load the scenario again.

#### Removing annotations/segments/mentions

This is currently not possible, a workaround is to put your data into version control and commit frequently. You can
edit the JSON files by hand to remove Segments/Annotations/Mentions, after doing so you need to reload the page.

#### Save and undo functionality

There is also no undo functionality, and also the Save buttons are not very intuitive. Take care to save often, and
follow the advice in the previous point and track your changes using version control. 

## Add custom Annotations

Custom annotations values can be added by creating a data class in the backend, a component for displaying and editing the data
in the frontend and supporting selection of the annotation in a couple of places. Follow the following instructions:

### Backend

##### Representation
Add a class representing the data of the custom annotation to the `gmrc/representation/annotation.py` module. Follow the
examples that can be found there, the simplest case being the `Display` annotation.

##### Backend

In the `Backend#create_annotation` annotation method add a case that creates an instance of the class with initial values.

##### Frontend

Add an interface corresponding the data class created the backend to the frontend representation in
`webapp/src/app/representation/annotation.ts`, and add a case to the `annotationDisplayValue` function in the same
file returning a short string representation of the annotation that can be used in labels in the GUI.

#### Angular component

Create an Angular component to display and edit the annotation:
In *webapp/* run

        ng generate component annotations-myannotationname

This will add a new component in `webapp/src/app/annotations-myannotationname` with an html template containing the
view of the annotation and a typescript component holding the data. The typescript class must contain a `data` field

        @Input() data: Annotation<MyAnnotataionType>;
        
that holds an Annotation with the custom annotation value in the `value` field and can be accessed in the html template.
Follow the patterns used in the other annotations, e.g. `webapp/src/app/annotations-person`.

Finally add the component to `webapp/src/app/component.service.ts`.