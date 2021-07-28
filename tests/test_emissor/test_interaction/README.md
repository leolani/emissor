
This module demonstrates how to use the ScenarioDriver to create a scenario by interaction and store it on disk.

To run the ScenarioDriver from command line:

python interactive_scenario_driver.py --scenario-folder <path to scenario folder> --scenario-id <name of the scenario>
After launching the ScenarioDriver (SC), a new scenario is added to the scenario folder with a unique scenarioId that needs to be provided through the command line argument.
A new folder is created in the scenario folder and the scenario.json is created.

The ScenarioDriver goes through the following interaction steps after creating and initialising a scenario:

1. Collect input signals at t1
- from command line
- from audio (@TODO)
- from camera (@TODO)

2. Process signals of t1 using listed processors  (@TODO)

3. Create signals and append to scenario with processor output

4. Update the BRAIN or query the BRAIN  (@TODO)

5. Create a response signal and append to scenario

6. Goto step 1

@TODO

1. allow for other input channels than the command line. Currently, the driver is just a chatbot
2. API for adding triple to the brain with the context information from the scenario (this replaces the capsule interface of the brain)
3. API for quering the BRAIN (is already there probably)
4. Initialise processors before running the interaction to that models are preloaded
5. Connect the input and output channels to backends for:
- pepper
- nao
- system
- others
  