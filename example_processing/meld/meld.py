from dataclasses import dataclass

from typing import Iterable, List

from emissor.representation.ldschema import emissor_dataclass
from emissor.representation.scenario import ScenarioContext

@emissor_dataclass
class MELDScenarioContext(ScenarioContext):
    season: int
    episode: int
    dialog_id: int
    speakers: List[str]
