
import logging
import spacy
import os
import time
import uuid
import cv2
from cv2 import VideoCapture
from datetime import datetime
from emissor.persistence import ScenarioStorage
from emissor.representation.scenario import Modality, ImageSignal, TextSignal, Mention, Annotation, Scenario

global capture,rec_frame, grey, switch, neg, face, rec, out
capture=0
grey=0
neg=0
face=0
switch=1
rec=0

def create_image_signal(scenario: Scenario, file: str):
    signal = ImageSignal.for_scenario(scenario.id, datetime.now().microsecond, datetime.now().microsecond, file, [], [])
    return signal

def create_text_signal(scenario: Scenario, utterance):
    signal = TextSignal.for_scenario(scenario.id, datetime.now().microsecond, datetime.now().microsecond, "./text.json", utterance, [])
    return signal

def create_scenario(scenarioPath: str, scenarioid: str):
    scenarioid = "myscenario2"
    scenario_path = "../../../data"
    myscenariopath = scenario_path+"/"+scenarioid
    if not os.path.exists(myscenariopath):
        os.mkdir(myscenariopath)
        print("Directory ", myscenariopath, " Created ")
    else:
        print("Directory ", myscenariopath, " already exists")
    imagefolder =  myscenariopath+"/"+"image"
    if not os.path.exists(imagefolder):
        os.mkdir(imagefolder)
        print("Directory ", imagefolder, " Created ")
    else:
        print("Directory ", imagefolder, " already exists")

    # so far not needed
    #textfolder = myscenariopath+"/"+"text"

    scenarioStorage = ScenarioStorage(scenario_path)
    return scenarioStorage

if __name__ == '__main__':
    logger = logging.getLogger(__name__)

    ##### Initialisation
    agent = "Leolani2"
    human = "Stranger"
    scenarioid = "myscenario2"
    scenario_path = "../../../data"
    imagefolder = scenario_path+"/"+scenarioid+"/"+"image"
    camera = cv2.VideoCapture(0)

    scenarioStorage = create_scenario(scenario_path, scenarioid)
    signals = {
        Modality.IMAGE.name.lower(): "./image.json",
        Modality.TEXT.name.lower(): "./text.json"
    }
    scenario = Scenario.new_instance(scenarioid, datetime.now().microsecond, datetime.now().microsecond, agent, signals)
    scenarioStorage.add_scenario(scenarioid, scenario)

    scenarioStorage.save_scenario(scenario)
    scenarioStorage.init_modality(Modality.TEXT)
    scenarioStorage.init_modality(Modality.IMAGE)

    ##### First signals to get started
    success, frame = camera.read()
    imagepath = ""
    if success:
        imagepath = imagefolder+"/"+ str(datetime.now().microsecond)+".png"
        cv2.imwrite(imagepath, frame)
    utterance = input(agent+": "+"Hi there. Who are you "+human+"?"+'\n\n')
    print(human+": "+utterance)

    while not (utterance.lower()=='stop' or utterance.lower()=='bye'):
        textSignal = create_text_signal(scenario, utterance)
        # @TODO
        ### Apply some processing to the textSignal and add annotations
        ### when done
        scenarioStorage.add_signal(Modality.TEXT, textSignal)
        response = utterance[::-1]
        print(agent+": "+response)

        if success:
            imageSignal = create_image_signal(scenario, imagepath)
            # @TODO
            ### Apply some processing to the imageSignal and add annotations
            ### when done

            scenarioStorage.add_signal(Modality.IMAGE, imageSignal)

        ###### Getting the next input signals
        utterance = input(agent+": "+"So  what do you want to talk about next?" + '\n')
        print("you: "+utterance)

        success, frame = camera.read()
        if success:
            imagepath = imagefolder + "/" + str(datetime.now().microsecond) + ".png"
            cv2.imwrite(imagepath, frame)



    #scenarioStorage.serialise_signals_all_modalities(scenarioid)
    scenarioStorage.serialise_signals(scenarioid, Modality.TEXT)
    #scenarioStorage.serialise_signals(scenarioid, Modality.IMAGE)