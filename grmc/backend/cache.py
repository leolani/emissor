class ScenarioCache(dict):
    def __init__(self, scenario_id: str) -> None:
        self.scenario_id = scenario_id

    def __setitem__(self, key, value):
        super().__setitem__(key, {signal.id: signal for signal in value})
