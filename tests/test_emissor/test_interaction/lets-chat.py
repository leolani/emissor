"""demo chat with Leolani. Leolani uses face recognition and gender/age
estimation.

Don't forget to install emissor by `pip install .` at the root of this repo.
Install the requirements `pip install -r requirements.txt`
you might also have to run `python -m spacy download en`

Occasionally you have to kill the docker containers if you force close the chat.
`docker kill $(docker ps -q)`

"""
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
from emissor.representation.scenario import (
    Modality,
    ImageSignal,
    TextSignal,
    Mention,
    Annotation,
    Scenario,
)
import cv2
import driver_util as util
import argparse
import python_on_whales
import logging
import requests
import numpy as np
import pickle
from PIL import Image, ImageDraw, ImageFont
from glob import glob

logging.basicConfig(
    level=os.environ.get("LOGLEVEL", "INFO").upper(),
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def cosine_similarity(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Compute the cosine similarity of the two vectors.

    Args
    ----
    x, y: vectors

    Returns
    -------
    similarity: a similarity score between -1 and 1, where 1 is the most
        similar.

    """

    similarity = np.dot(x, y) / (np.sqrt(np.dot(x, x)) * np.sqrt(np.dot(y, y)))

    return similarity


def start_docker_container(
    image: str, port_id: int, sleep_time=5
) -> python_on_whales.Container:
    """Start docker container given the image name and port number.

    Args
    ----
    image: docker image name
    port_id: port id
    sleep_time: warmup time

    Returns
    -------
    container: a docker container object.

    """
    container = python_on_whales.docker.run(
        image=image, detach=True, publish=[(port_id, port_id)]
    )

    logging.info(f"starting a {image} container ...")
    logging.debug(f"warming up the container ...")
    time.sleep(sleep_time)

    return container


def kill_container(container: python_on_whales.Container) -> None:
    """Kill docker container.

    Args
    ----
    container:
        a docker container object.

    """
    container.kill()
    logging.info(f"container killed.")
    logging.info(f"DONE!")


def unpickle(path: str):
    """Unpickle the pickled file, and return it.

    Args
    ----
    path: path to the pickle

    Returns
    -------
    returned: un unpickled object to be returned.

    """
    with open(path, "rb") as stream:
        returned = pickle.load(stream)

    return returned


def load_embeddings(paths: str = "./embeddings/*.pkl") -> dict:
    """Load pre-defined face embeddings.

    Args
    ----
    paths: paths to the face embedding vectors.

    Returns
    -------
    embeddings_predefined: predefined embeddings

    """
    embeddings_predefined = {}
    for path in glob(paths):
        name = path.split("/")[-1].split(".pkl")[0]
        unpickled = unpickle(path)

        embeddings_predefined[unpickled["uuid"]] = {
            "embedding": unpickled["embedding"],
            "name": name,
        }

    return embeddings_predefined


def face_recognition(embeddings: list, COSINE_SIMILARITY_THRESHOLD=0.65) -> list:
    """Perform face recognition based on the cosine similarity.

    Args
    ----
    embeddings: a list of embeddings
    COSINE_SIMILARITY_THRESHOLD: Currently fixed to The cosine similarity
        threshold is fixed to 0.65. Feel free to play around with this number.

    Returns
    -------
        faces_detected: list of faces (uuids and names) detected.

    """
    embeddings_predefined = load_embeddings()

    cosine_similarities = []
    for embedding in embeddings:
        cosine_similarities_ = {
            uuid_
            + " "
            + embedding_name["name"]: cosine_similarity(
                embedding, embedding_name["embedding"]
            )
            for uuid_, embedding_name in embeddings_predefined.items()
        }
        cosine_similarities.append(cosine_similarities_)

    logging.debug(f"cosine similarities: {cosine_similarities}")

    faces_detected_ = [max(sim, key=sim.get) for sim in cosine_similarities]
    faces_detected = []
    for uuid_name, sim in zip(faces_detected_, cosine_similarities):
        uuid_, name = uuid_name.split()
        if sim[uuid_name] > COSINE_SIMILARITY_THRESHOLD:
            faces_detected.append({"uuid": uuid_, "name": name})
        else:
            logging.info("new face!")
            faces_detected.append({"uuid": str(uuid.uuid4()), "name": None})
            pass

    return faces_detected


def load_binary_image(image_path: str) -> bytes:
    """Load encoded image as a binary string and return it.

    Args
    ----
    image_path: path to the image to load.

    Returns
    -------
    binary_image: encoded binary image in bytes

    """
    logging.debug(f"{image_path} loading image ...")
    with open(image_path, "rb") as stream:
        binary_image = stream.read()
    logging.info(f"{image_path} image loaded!")

    return binary_image


def run_face_api(to_send: dict, url_face: str = "http://127.0.0.1:10002/") -> tuple:
    """Make a RESTful HTTP request to the face API server.

    Args
    ----
    to_send: dictionary to send to the server. In this function, this will be
        encoded with jsonpickle. I know this is not conventional, but encoding
        and decoding is so easy with jsonpickle somehow.
    url_face: the url of the face recognition server.

    Returns
    -------
    bboxes: (list) boudning boxes
    det_scores: (list) detection scores
    landmarks: (list) landmarks
    embeddings: (list) face embeddings
    """
    logging.debug(f"sending image to server...")
    to_send = jsonpickle.encode(to_send)
    response = requests.post(url_face, json=to_send)
    logging.info(f"got {response} from server!...")
    response = jsonpickle.decode(response.text)

    face_detection_recognition = response["face_detection_recognition"]
    logging.info(f"{len(face_detection_recognition)} faces deteced!")

    bboxes = [fdr["bbox"] for fdr in face_detection_recognition]
    det_scores = [fdr["det_score"] for fdr in face_detection_recognition]
    landmarks = [fdr["landmark"] for fdr in face_detection_recognition]

    embeddings = [fdr["normed_embedding"] for fdr in face_detection_recognition]

    return bboxes, det_scores, landmarks, embeddings


def run_age_gender_api(
    embeddings: list, url_age_gender: str = "http://127.0.0.1:10003/"
) -> tuple:
    """Make a RESTful HTTP request to the age-gender API server.

    Args
    ----
    embeddings: a list of embeddings. The number of elements in this list is
        the number of faces detected in the frame.
    url_age_gender: the url of the age-gender API server.

    Returns
    -------
    ages: (list) a list of ages
    genders: (list) a list of genders.

    """
    # -1 accounts for the batch size.
    data = np.array(embeddings).reshape(-1, 512).astype(np.float32)
    data = pickle.dumps(data)

    data = {"embeddings": data}
    data = jsonpickle.encode(data)
    logging.debug(f"sending embeddings to server ...")
    response = requests.post(url_age_gender, json=data)
    logging.info(f"got {response} from server!...")

    response = jsonpickle.decode(response.text)
    ages = response["ages"]
    genders = response["genders"]

    return ages, genders


def do_stuff_with_image(
    image_path: str,
    url_face: str = "http://127.0.0.1:10002/",
    url_age_gender: str = "http://127.0.0.1:10003/",
) -> tuple:
    """Do stuff with image.

    Args
    ----
    image_path: path to the image in disk
    url_face: the url of the face recognition server.
    url_age_gender: the url of the age-gender API server.

    Returns
    -------
    genders
    ages
    bboxes
    faces_detected
    det_scores
    embeddings

    """
    MAXIMUM_ENTROPY = {"gender": 0.6931471805599453, "age": 4.615120516841261}

    data = {"image": load_binary_image(image_path)}

    bboxes, det_scores, landmarks, embeddings = run_face_api(data, url_face)

    faces_detected = face_recognition(embeddings)

    ages, genders = run_age_gender_api(embeddings, url_age_gender)

    logging.debug("annotating image ...")
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("fonts/arial.ttf", 25)

    assert (
        len(genders)
        == len(ages)
        == len(bboxes)
        == len(faces_detected)
        == len(det_scores)
    )
    for gender, age, bbox, uuid_name, faceprob in zip(
        genders, ages, bboxes, faces_detected, det_scores
    ):
        draw.rectangle(bbox.tolist(), outline=(0, 0, 0))

        draw.text(
            (bbox[0], bbox[1]),
            f"{str(uuid_name['name']).replace('_', ' ')}, {round(age['mean'])} years old",
            fill=(255, 0, 0),
            font=font,
        )

        draw.text(
            (bbox[0], bbox[3]),
            "MALE " + str(round(gender["m"] * 100)) + str("%") + ", "
            "FEMALE " + str(round(gender["f"] * 100)) + str("%"),
            fill=(0, 255, 0),
            font=font,
        )

        image.save(image_path + ".ANNOTATED.jpg")
    logging.debug(f"image annotated and saved at {image_path + '.ANNOTATED.jpg'}")

    return genders, ages, bboxes, faces_detected, det_scores, embeddings


def main(agent: str, human: str, scenario_path: str, webcam_id: int) -> None:
    """A dummy dialogue with face recognition and gender/age estimation.

    Args
    ----
    agent: the name of the chatbot that you are talking to.
    human: your (human) name.
    scenario_path: directory path to save the dialogue history with images.
    webcam_id: webcam id (e.g., 0)

    """
    container_fdr = start_docker_container("tae898/face-detection-recognition:v0.1", 10002)
    container_ag = start_docker_container("tae898/age-gender:v0.2", 10003)

    scenario_id = datetime.today().strftime("%Y-%m-%d-%H:%M:%S")
    os.makedirs(scenario_path, exist_ok=True)
    # Define the folder where the images are saved
    imagefolder = scenario_path + "/" + scenario_id + "/" + "image"

    # Link your camera
    camera = cv2.VideoCapture(webcam_id)

    # Load a language model in spaCy
    nlp = spacy.load("en_core_web_sm")

    # Create the scenario folder, the json files and a scenarioStorage and scenario in memory
    scenarioStorage = util.create_scenario(scenario_path, scenario_id)
    scenario = scenarioStorage.create_scenario(
        scenario_id, datetime.now().microsecond, datetime.now().microsecond, agent
    )

    # Example of an annotation function that adds annotations to a Signal
    def add_ner_annotation(signal: TextSignal):
        processor_name = "spaCy"
        utterance = "".join(signal.seq)

        doc = nlp(utterance)

        offsets, tokens = zip(
            *[
                (
                    Index(signal.id, token.idx, token.idx + len(token)),
                    Token.for_string(token.text),
                )
                for token in doc
            ]
        )

        ents = [NER.for_string(ent.label_) for ent in doc.ents]
        entity_text = [ent.text for ent in doc.ents]
        segments = [token.ruler for token in tokens if token.value in entity_text]

        annotations = [
            Annotation(
                AnnotationType.TOKEN.name.lower(),
                token,
                processor_name,
                int(time.time()),
            )
            for token in tokens
        ]
        ner_annotations = [
            Annotation(
                AnnotationType.NER.name.lower(), ent, processor_name, int(time.time())
            )
            for ent in ents
        ]

        signal.mentions.extend(
            [
                Mention(str(uuid.uuid4()), [offset], [annotation])
                for offset, annotation in zip(offsets, annotations)
            ]
        )
        signal.mentions.extend(
            [
                Mention(str(uuid.uuid4()), [segment], [annotation])
                for segment, annotation in zip(segments, ner_annotations)
            ]
        )

        return entity_text

    # First signals to get started
    success, frame = camera.read()
    imagepath = ""
    if success:
        current_time = str(datetime.now().microsecond)
        imagepath = imagefolder + "/" + current_time + ".png"
        cv2.imwrite(imagepath, frame)
        (
            genders,
            ages,
            bboxes,
            faces_detected,
            det_scores,
            embeddings,
        ) = do_stuff_with_image(imagepath)

    # Initial prompt by the system from which we create a TextSignal and store it

    # Here we assume that only one face is in the image
    # TODO: deal with multiple people.
    for k, (gender, age, bbox, uuid_name, faceprob, embedding) in enumerate(
        zip(genders, ages, bboxes, faces_detected, det_scores, embeddings)
    ):
        age = round(age["mean"])
        gender = "male" if gender["m"] > 0.5 else "female"
        bbox = [int(num) for num in bbox.tolist()]

    assert k == 0

    if uuid_name["name"] is None:
        response = (
            f"Hi there. We haven't met each other. I only know that "
            f"your estimated age is {age} and that your estimated gender is "
            f"{gender}. What's your name?"
        )
        print(f"{agent}: {response}")
        textSignal = util.create_text_signal(scenario, response)
        scenario.append_signal(textSignal)

        utterance = input("\n")
        textSignal = util.create_text_signal(scenario, utterance)
        scenario.append_signal(textSignal)

        new_name = " ".join([foo.title() for foo in utterance.strip().split()])
        print(agent + f": Nice to meet you, {new_name}")

        to_save = {"uuid": uuid_name["uuid"], "embedding": embedding}

        new_name = "_".join(new_name.split())
        with open(f"./embeddings/{new_name}.pkl", "wb") as stream:
            pickle.dump(to_save, stream)

    else:
        response = f"Hi {uuid_name['name']}. Nice to see you again :)"
        print(f"{agent}: {response}")
        textSignal = util.create_text_signal(scenario, response)
        scenario.append_signal(textSignal)

    response = "How are you doing?"
    textSignal = util.create_text_signal(scenario, response)
    scenario.append_signal(textSignal)

    print(agent + ": " + response)

    utterance = input("\n")
    print(human + ": " + utterance)

    while not (utterance.lower() == "stop" or utterance.lower() == "bye"):
        textSignal = util.create_text_signal(scenario, utterance)
        # @TODO
        # Apply some processing to the textSignal and add annotations
        entityText = add_ner_annotation(textSignal)

        scenario.append_signal(textSignal)

        if success:
            imageSignal = util.create_image_signal(scenario, imagepath)
            container_id = str(uuid.uuid4())

            for gender, age, bbox, name, faceprob in zip(
                genders, ages, bboxes, faces_detected, det_scores
            ):

                age = round(age["mean"])
                gender = "male" if gender["m"] > 0.5 else "female"
                bbox = [int(num) for num in bbox.tolist()]

                annotations = []

                annotations.append(
                    {
                        "source": "machine",
                        "timestamp": current_time,
                        "type": "person",
                        "value": {
                            "name": name,
                            "age": age,
                            "gender": gender,
                            "faceprob": faceprob,
                        },
                    }
                )

                mention_id = str(uuid.uuid4())
                segment = [
                    {"bounds": bbox, "container_id": container_id, "type": "MultiIndex"}
                ]
                imageSignal.mentions.append(
                    {"annotations": annotations, "id": mention_id, "segment": segment}
                )

            scenario.append_signal(imageSignal)

        # Create the response from the system and store this as a new signal

        if not entityText:
            utterance = "Any gossip" + "\n"
        else:
            utterance = "So you what do you want to talk about " + entityText[0] + "\n"

        response = utterance[::-1]
        print(agent + ": " + utterance)
        textSignal = util.create_text_signal(scenario, utterance)
        scenario.append_signal(textSignal)

        # Getting the next input signals
        utterance = input("\n")

        success, frame = camera.read()
        if success:
            current_time = str(datetime.now().microsecond)
            imagepath = imagefolder + "/" + current_time + ".png"
            cv2.imwrite(imagepath, frame)
            (
                genders,
                ages,
                bboxes,
                faces_detected,
                det_scores,
                embeddings,
            ) = do_stuff_with_image(imagepath)

    scenarioStorage.save_scenario(scenario)

    kill_container(container_fdr)
    kill_container(container_ag)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="lets-chat")
    parser.add_argument("--agent", type=str, default="Leolani")
    parser.add_argument("--human", type=str, default="Human")
    parser.add_argument("--scenario-path", type=str, default="./scenarios")
    parser.add_argument(
        "--webcam-id",
        type=int,
        default=0,
        help="ffplay /dev/video0 to confirm the webcam id",
    )

    args = vars(parser.parse_args())
    print("Arguments:")
    for key, val in args.items():
        print(f"  {key:>21} : {val}")
    main(**args)
