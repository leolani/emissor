import {Injectable} from '@angular/core';
import {InMemoryDbService} from 'angular-in-memory-web-api';

@Injectable({
  providedIn: 'root',
})
export class InMemoryDataService implements InMemoryDbService {
  createDb() {
    const scenario = [
      {
        "start": 1603139000,
        "end": 1603150000,
        "id": "scenario_1",
        "context": {
          "agent": "robot_agent",
          "speaker": {
            "id": "1007e3ef-10c4-43db-8f6d-e9635fb0173f",
            "name": "Speaker",
            "age": 50,
            "gender": "UNDEFINED"
          },
          "persons": [],
          "objects": []
        },
        "signals": {
          "image": "./image.json",
          "text": "./text.json"
        }
      },
      {
        "start": 0,
        "end": 120,
        "id": "scenario_2",
        "ruler": {
          "type": "TemporalRuler",
          "container_id": "scenario_2",
          "start": 0,
          "end": 120
        },
        "context": {
          "agent": "robot_agent",
          "speaker": {
            "id": "1007e3ef-10c4-43db-8f6d-e9635fb0173f",
            "name": "Speaker",
            "age": 50,
            "gender": "UNDEFINED"
          },
          "persons": [],
          "objects": []
        },
        "signals": {
          "image": "./image.json",
          "text": "./text.json"
        }
      }
    ];

    const image = [
      {
        "modality": "IMAGE",
        "time": {
          "type": "TemporalRuler",
          "container_id": "scenario_1",
          "start": 1603140000,
          "end": 1603140000
        },
        "files": [
          "./image/piek-sunglasses.jpg"
        ],
        "mentions": [
          {
            "segment": [{
              "type": "MultiIndex",
              "container_id": "c0bf19da-ee25-4f6e-bcb5-3d8f29943e31",
              "bounds": [10, 15, 52, 51]
            }],
            "annotations": [
              {
                "type": "Friend",
                "value": {
                  "id": "862c4e60-f822-47c1-94db-9eabe13f74ef",
                  "name": "Piek",
                  "age": 59,
                  "gender": "MALE"
                },
                "source": "face_recognition",
                "timestamp": 1605002193.87345
              },
              {
                "type": "Emotion",
                "value": "JOY",
                "source": "annotator_1",
                "timestamp": 1605002193.873485
              },
              {
                "type": "Display",
                "value": "Piek",
                "source": "annotator_1",
                "timestamp": 1605002193.873485
              }
            ]
          }
        ],
        "array": null,
        "id": "c0bf19da-ee25-4f6e-bcb5-3d8f29943e31",
      },
      {
        "modality": "IMAGE",
        "time": {
          "type": "TemporalRuler",
          "container_id": "scenario_1",
          "start": 1603139705,
          "end": 1603140000
        },
        "files": [
          "./image/maxima.jpg"
        ],
        "mentions": [],
        "array": null,
        "id": "163b27da-ee25-4f6e-bcb5-4d7a12236a52",
      }];

    const text = [
      {
        "modality": "TEXT",
        "time": {
          "type": "TemporalRuler",
          "container_id": "scenario_1",
          "start": 1603139705,
          "end": 1603140000
        },
        "files": [],
        "mentions": [
          {
            "segment": [{
              "type": "Index",
              "container_id": "a6ecd306-e78a-4dd5-ba55-aa9827050e07",
              "start": 0,
              "stop": 4
            }],
            "annotations": [
              {
                "type": "Token",
                "value": {
                  "value": "That",
                  "id": "e9ec8f59-a271-44c3-a385-7d9b86051ba1",
                  "ruler": {
                    "type": "AtomicRuler",
                    "container_id": "e9ec8f59-a271-44c3-a385-7d9b86051ba1"
                  }
                },
                "source": "treebank_tokenizer",
                "timestamp": 1605002193.8999848
              }
            ]
          },
          {
            "segment": [{
              "type": "Index",
              "container_id": "a6ecd306-e78a-4dd5-ba55-aa9827050e07",
              "start": 5,
              "stop": 7
            }],
            "annotations": [
              {
                "type": "Token",
                "value": {
                  "value": "is",
                  "id": "0c35647b-10fe-4eea-825f-171ccda256f5",
                  "ruler": {
                    "type": "AtomicRuler",
                    "container_id": "0c35647b-10fe-4eea-825f-171ccda256f5"
                  }
                },
                "source": "treebank_tokenizer",
                "timestamp": 1605002193.899989
              }
            ]
          },
          {
            "segment": [{
              "type": "Index",
              "container_id": "a6ecd306-e78a-4dd5-ba55-aa9827050e07",
              "start": 8,
              "stop": 10
            }],
            "annotations": [
              {
                "type": "Token",
                "value": {
                  "value": "my",
                  "id": "fc407058-92e6-4157-8e91-2217665f052f",
                  "ruler": {
                    "type": "AtomicRuler",
                    "container_id": "fc407058-92e6-4157-8e91-2217665f052f"
                  }
                },
                "source": "treebank_tokenizer",
                "timestamp": 1605002193.89999
              }
            ]
          },
          {
            "segment": [{
              "type": "Index",
              "container_id": "a6ecd306-e78a-4dd5-ba55-aa9827050e07",
              "start": 11,
              "stop": 18
            }],
            "annotations": [
              {
                "type": "Token",
                "value": {
                  "value": "brother",
                  "id": "a47357c5-faf3-4420-a675-8aaebb1b0707",
                  "ruler": {
                    "type": "AtomicRuler",
                    "container_id": "a47357c5-faf3-4420-a675-8aaebb1b0707"
                  }
                },
                "source": "treebank_tokenizer",
                "timestamp": 1605002193.899991
              }
            ]
          },
          {
            "segment": [{
              "type": "Index",
              "container_id": "a6ecd306-e78a-4dd5-ba55-aa9827050e07",
              "start": 19,
              "stop": 22
            }],
            "annotations": [
              {
                "type": "Token",
                "value": {
                  "value": "Jim",
                  "id": "2566aa47-5f36-455a-9582-bda4aeaeaf6f",
                  "ruler": {
                    "type": "AtomicRuler",
                    "container_id": "2566aa47-5f36-455a-9582-bda4aeaeaf6f"
                  }
                },
                "source": "treebank_tokenizer",
                "timestamp": 1605002193.899992
              }
            ]
          }
        ],
        "seq": "That is my brother Jim",
        "id": "a6ecd306-e78a-4dd5-ba55-aa9827050e07"
      }
    ];

    return {scenario, image, text};
  }
}
