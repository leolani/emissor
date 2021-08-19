import jsonpickle
import emissor as em
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
import driver_util as util
import argparse
from python_on_whales import docker
import logging
import requests
import numpy as np
import pickle
from PIL import Image
from PIL import Image, ImageDraw, ImageFont

logging.basicConfig(level=logging.DEBUG)


def start_docker_container(image, port_id):
    container = docker.run(image=image,
                           detach=True,
                           publish=[(port_id, port_id)])

    logging.info(f"starting a {image} container ...")
    logging.debug(f"warming up the container ...")
    time.sleep(5)

    return container


def kill_container(container):
    container.kill()
    logging.info(f"container killed.")
    logging.info(f"DONE!")


def do_stuff_with_image(image_path,
                        url_face='http://127.0.0.1:10002/',
                        url_age_gender='http://127.0.0.1:10003/'):

    MAXIMUM_ENTROPY = {'gender': 0.6931471805599453,
                       'age': 4.615120516841261}

    logging.debug(f"{image_path} loading image ...")
    with open(image_path, 'rb') as stream:
        binary_image = stream.read()

    data = {'image': binary_image}
    logging.info(f"image loaded!")

    logging.debug(f"sending image to server...")
    data = jsonpickle.encode(data)
    response = requests.post(url_face, json=data)
    logging.info(f"got {response} from server!...")
    response = jsonpickle.decode(response.text)

    face_detection_recognition = response['face_detection_recognition']
    logging.info(f"{len(face_detection_recognition)} faces deteced!")

    bboxes = [fdr['bbox'] for fdr in face_detection_recognition]
    det_scores = [fdr['det_score'] for fdr in face_detection_recognition]
    landmarks = [fdr['landmark'] for fdr in face_detection_recognition]

    logging.debug(f"sending embeddings to server ...")
    data = [fdr['normed_embedding'] for fdr in face_detection_recognition]

    # -1 accounts for the batch size.
    data = np.array(data).reshape(-1, 512).astype(np.float32)

    # I wanna get rid of this pickling part but dunno how.
    data = pickle.dumps(data)

    data = {'embeddings': data}
    data = jsonpickle.encode(data)
    response = requests.post(url_age_gender, json=data)
    logging.info(f"got {response} from server!...")

    response = jsonpickle.decode(response.text)
    ages = response['ages']
    genders = response['genders']

    logging.debug(f"annotating image ...")
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("fonts/arial.ttf", 25)

    for gender, age, bbox in zip(genders, ages, bboxes):
        draw.rectangle(bbox.tolist(), outline=(0, 0, 0))
        draw.text(
            (bbox[0], bbox[1]), f"AGE: {round(age['mean'])} (entropy: {round(age['entropy'], 3)} / {round(MAXIMUM_ENTROPY['age'], 3)})", fill=(255, 0, 0), font=font)
        draw.text((bbox[0], bbox[3]), 'MALE ' + str(round(gender['m']*100)) + str("%") +
                  ', ' 'FEMALE ' + str(round(gender['f']*100)) + str("%") + f" (entropy: {round(gender['entropy'], 3)} / {round(MAXIMUM_ENTROPY['gender'], 3)})", fill=(0, 255, 0), font=font)
        image.save(image_path + '.ANNOTATED.jpg')
    logging.debug(
        f"image annotated and saved at {image_path + '.ANNOTATED.jpg'}")


def main(agent, human, scenario_path):

    container_fdr = start_docker_container(
        'tae898/face-detection-recognition', 10002)
    container_ag = start_docker_container('tae898/age-gender', 10003)

    scenario_id = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
    os.makedirs(scenario_path, exist_ok=True)
    # Define the folder where the images are saved
    imagefolder = scenario_path + "/" + scenario_id + "/" + "image"

    # Link your camera
    camera = cv2.VideoCapture(0)

    # Load a language model in spaCy
    nlp = spacy.load('en_core_web_sm')

    # Create the scenario folder, the json files and a scenarioStorage and scenario in memory
    scenarioStorage = util.create_scenario(scenario_path, scenario_id)
    scenario = scenarioStorage.create_scenario(
        scenario_id, datetime.now().microsecond, datetime.now().microsecond, agent)

    # Example of an annotation function that adds annotations to a Signal
    def add_ner_annotation(signal: TextSignal):
        processor_name = "spaCy"
        utterance = ''.join(signal.seq)

        doc = nlp(utterance)

        offsets, tokens = zip(*[(Index(signal.id, token.idx, token.idx + len(token)), Token.for_string(token.text))
                                for token in doc])

        ents = [NER.for_string(ent.label_) for ent in doc.ents]
        entity_text = [ent.text for ent in doc.ents]
        segments = [
            token.ruler for token in tokens if token.value in entity_text]

        annotations = [Annotation(AnnotationType.TOKEN.name.lower(), token, processor_name, int(time.time()))
                       for token in tokens]
        ner_annotations = [Annotation(AnnotationType.NER.name.lower(), ent, processor_name, int(time.time()))
                           for ent in ents]

        signal.mentions.extend([Mention(str(uuid.uuid4()), [offset], [annotation])
                                for offset, annotation in zip(offsets, annotations)])
        signal.mentions.extend([Mention(str(uuid.uuid4()), [segment], [annotation])
                                for segment, annotation in zip(segments, ner_annotations)])

        return entity_text

    # First signals to get started
    success, frame = camera.read()
    imagepath = ""
    if success:
        imagepath = imagefolder + "/" + \
            str(datetime.now().microsecond) + ".png"
        cv2.imwrite(imagepath, frame)
        do_stuff_with_image(imagepath)

    # Initial prompt by the system from which we create a TextSignal and store it
    response = "Hi there. Who are you " + human + "?"
    print(agent + ": " + response)
    textSignal = util.create_text_signal(scenario, response)
    scenario.append_signal(textSignal)

    utterance = input('\n')
    print(human + ": " + utterance)

    while not (utterance.lower() == 'stop' or utterance.lower() == 'bye'):
        textSignal = util.create_text_signal(scenario, utterance)
        # @TODO
        # Apply some processing to the textSignal and add annotations
        entityText = add_ner_annotation(textSignal)

        scenario.append_signal(textSignal)

        if success:
            imageSignal = util.create_image_signal(scenario, imagepath)
            # @TODO
            # Apply some processing to the imageSignal and add annotations
            # when done

            scenario.append_signal(imageSignal)

        # Create the response from the system and store this as a new signal

        if not entityText:
            utterance = "Any gossip" + '\n'
        else:
            utterance = "So you what do you want to talk about " + \
                entityText[0] + '\n'

        response = utterance[::-1]
        print(agent + ": " + utterance)
        textSignal = util.create_text_signal(scenario, utterance)
        scenario.append_signal(textSignal)

        # Getting the next input signals
        utterance = input('\n')

        success, frame = camera.read()
        if success:
            imagepath = imagefolder + "/" + \
                str(datetime.now().microsecond) + ".png"
            cv2.imwrite(imagepath, frame)
            do_stuff_with_image(imagepath)

    scenarioStorage.save_scenario(scenario)

    kill_container(container_fdr)
    kill_container(container_ag)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='lets-chat')
    parser.add_argument('--agent', type=str, default='Leolani2')
    parser.add_argument('--human', type=str, default='Stranger')
    parser.add_argument('--scenario-path', type=str, default='./scenarios')

    args = parser.parse_args()
    args = vars(args)

    main(**args)
