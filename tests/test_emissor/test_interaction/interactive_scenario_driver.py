
import logging
import os
import cv2
from datetime import datetime
from emissor.persistence import ScenarioStorage
from emissor.representation.scenario import Modality, ImageSignal, TextSignal, Mention, Annotation, Scenario
import tests.test_emissor.test_interaction.driver_util as util

if __name__ == '__main__':
    logger = logging.getLogger(__name__)

    ##### Initialisation
    agent = "Leolani2"
    human = "Stranger"
    scenarioid = "myscenario3"
    scenario_path = "../../../data"
    imagefolder = scenario_path+"/"+scenarioid+"/"+"image"
    camera = cv2.VideoCapture(0)

    scenarioStorage = util.create_scenario(scenario_path, scenarioid)
    scenario = scenarioStorage.create_scenario(scenarioid, datetime.now().microsecond, datetime.now().microsecond, agent)

    ##### First signals to get started
    success, frame = camera.read()
    imagepath = ""
    if success:
        imagepath = imagefolder+"/"+ str(datetime.now().microsecond)+".png"
        cv2.imwrite(imagepath, frame)

    #### Initial prompt by the system from which we create a TextSignal and store it
    response = "Hi there. Who are you "+human+"?"
    print(agent + ": " + response)
    textSignal = util.create_text_signal(scenario, response)
    scenario.append_signal(textSignal)
    
    utterance = input('\n')
    print(human+": "+utterance)

    while not (utterance.lower()=='stop' or utterance.lower()=='bye'):
        textSignal = util.create_text_signal(scenario, utterance)
        # @TODO
        ### Apply some processing to the textSignal and add annotations
        ### when done
        scenario.append_signal(textSignal)

        if success:
            imageSignal = util.create_image_signal(scenario, imagepath)
            # @TODO
            ### Apply some processing to the imageSignal and add annotations
            ### when done

            scenario.append_signal(imageSignal)

        # Create the response from the system and store this as a new signal
        response = utterance[::-1]
        print(agent + ": " + response)
        textSignal = util.create_text_signal(scenario, response)
        scenario.append_signal(textSignal)

        ###### Getting the next input signals
        utterance = input('\n')

        success, frame = camera.read()
        if success:
            imagepath = imagefolder + "/" + str(datetime.now().microsecond) + ".png"
            cv2.imwrite(imagepath, frame)


    scenarioStorage.save_scenario(scenario)