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
            "segment": {
              "type": "MultiIndex",
              "container_id": "c0bf19da-ee25-4f6e-bcb5-3d8f29943e31",
              "bounds": [[10, 521], [15, 518]]
            },
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
        "mentions": [],
        "seq": "Hello world",
        "id": "163b27da-ee25-4f6e-bcb5-4d7a12236a52",
      }
    ];

    return {scenario, image, text};
  }
}
