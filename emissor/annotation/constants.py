import uuid

from emissor.representation.entity import Person, Gender
from emissor.representation.scenario import Modality

SPEAKER = Person(str(uuid.uuid4()), "Speaker", 50, Gender.UNDEFINED)
DEFAULT_SIGNALS = {
    Modality.IMAGE.name.lower(): "./image.json",
    Modality.TEXT.name.lower(): "./text.json"
}
