
import logging
import os
import spacy
import time
import uuid
from datetime import datetime
from emissor.persistence import ScenarioStorage
from emissor.representation.annotation import AnnotationType, Token, NER
from emissor.representation.container import Index
from emissor.representation.scenario import Modality, ImageSignal, TextSignal, Mention, Annotation, Scenario
import cv2
from datetime import datetime

def create_image_signal(scenario: Scenario, file: str):
    signal = ImageSignal.for_scenario(scenario.id, datetime.now().microsecond, datetime.now().microsecond, file, [], [])
    return signal

def create_text_signal(scenario: Scenario, utterance):
    signal = TextSignal.for_scenario(scenario.id, datetime.now().microsecond, datetime.now().microsecond, "./text.json", utterance, [])
    return signal

def create_scenario(scenarioPath: str, scenarioid: str):
    myscenariopath = scenarioPath+"/"+scenarioid
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



def add_ner_annotation(signal: TextSignal):
    processor_name = "spaCy"
    utterance = ''.join(signal.seq)

    doc = nlp(utterance)

    offsets, tokens = zip(*[(Index(signal.id, token.idx, token.idx + len(token)), Token.for_string(token.text))
                            for token in doc])

    ents = [NER.for_string(ent.label_) for ent in doc.ents]
    entity_text = [ent.text for ent in doc.ents]
    segments = [token.ruler for token in tokens if token.value in entity_text]

    annotations = [Annotation(AnnotationType.TOKEN.name.lower(), token, processor_name, int(time.time()))
                   for token in tokens]
    ner_annotations = [Annotation(AnnotationType.NER.name.lower(), ent, processor_name, int(time.time()))
                       for ent in ents]

    signal.mentions.extend([Mention(str(uuid.uuid4()), [offset], [annotation])
                            for offset, annotation in zip(offsets, annotations)])
    signal.mentions.extend([Mention(str(uuid.uuid4()), [segment], [annotation])
                            for segment, annotation in zip(segments, ner_annotations)])

    return entity_text


if __name__ == '__main__':
        logger = logging.getLogger(__name__)

        ##### Initialisation
        agent = "Leolani2"
        human = "Stranger"
        scenarioid = "myscenario3"
        scenario_path = "../../../data"
        imagefolder = scenario_path + "/" + scenarioid + "/" + "image"
        camera = cv2.VideoCapture(0)
        nlp = spacy.load('en_core_web_sm')

        scenarioStorage = create_scenario(scenario_path, scenarioid)
        scenario = scenarioStorage.create_scenario(scenarioid, datetime.now().microsecond, datetime.now().microsecond, agent)

        ##### First signals to get started
        success, frame = camera.read()
        imagepath = ""
        if success:
            imagepath = imagefolder + "/" + str(datetime.now().microsecond) + ".png"
            cv2.imwrite(imagepath, frame)

        #### Initial prompt by the system from which we create a TextSignal and store it
        response = "Hi there. Who are you " + human + "?"
        print(agent + ": " + response)
        textSignal = create_text_signal(scenario, response)
        scenario.append_signal(textSignal)

        utterance = input('\n')
        print(human + ": " + utterance)

        while not (utterance.lower() == 'stop' or utterance.lower() == 'bye'):
            textSignal = create_text_signal(scenario, utterance)
            # @TODO
            ### Apply some processing to the textSignal and add annotations
            entityText = add_ner_annotation(textSignal)

            scenario.append_signal(textSignal)

            if success:
                imageSignal = create_image_signal(scenario, imagepath)
                # @TODO
                ### Apply some processing to the imageSignal and add annotations
                ### when done

                scenario.append_signal(imageSignal)

            # Create the response from the system and store this as a new signal

            if not entityText:
                utterance = "Any gossip" + '\n'
            else:
                utterance = "So you what do you want to talk about" + entityText[0] + '\n'

            response = utterance[::-1]
            print(agent + ": " + utterance)
            textSignal = create_text_signal(scenario, utterance)
            scenario.append_signal(textSignal)

            ###### Getting the next input signals
            utterance = input('\n')

            success, frame = camera.read()
            if success:
                imagepath = imagefolder + "/" + str(datetime.now().microsecond) + ".png"
                cv2.imwrite(imagepath, frame)

        scenarioStorage.save_scenario(scenario)


