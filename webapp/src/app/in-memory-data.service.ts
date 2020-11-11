import { Injectable } from '@angular/core';
import { InMemoryDbService } from 'angular-in-memory-web-api';
import { Signal } from './scenario'
import {printLine} from "tslint/lib/verify/lines";

@Injectable({
  providedIn: 'root',
})
export class InMemoryDataService implements InMemoryDbService {
  createDb() {
    const scenario = [
      { id: 1, path: "1", name: "scenario_1", start: 0, end: 110, modalities: {image: "image", text: "text"}}
    ];

    const image = [
      { id: 11, name: 'Dr Nice', timestamp: 0, image: "assets/testimages/maxima.jpg"},
      { id: 12, name: 'Narco', timestamp: 1, image: "assets/testimages/piek-sunglasses.jpg" },
      { id: 13, name: 'Bombasto', timestamp: 2, image: "assets/testimages/soccer-balll.png" },
      { id: 14, name: 'Celeritas', timestamp: 10, image: "assets/testimages/niqee-2020-10-25 at 17.30.51.png" },
      { id: 15, name: 'Magneta', timestamp: 12, image: "assets/testimages/maxima.jpg" },
      { id: 16, name: 'RubberMan', timestamp: 22, image: "assets/testimages/soccer-balll.png" },
      { id: 17, name: 'Dynama', timestamp: 34, image: "assets/testimages/piek-sunglasses.jpg" },
      { id: 18, name: 'Dr IQ', timestamp: 60, image: "assets/testimages/sam-2020-10-25 at 17.30.25.png" },
      { id: 19, name: 'Magma', timestamp: 100, image: "assets/testimages/piek-sunglasses.jpg" },
      { id: 20, name: 'Tornado', timestamp: 101, image: "assets/testimages/soccer-balll.png" }
    ];

    const text = [
      { id: 11, text: "Bla bla bla", timestamp: 15 },
      { id: 12, text: "Bla bla bla", timestamp: 35 },
      { id: 13, text: "Bla bla bla", timestamp: 45 },
      { id: 14, text: "Bla bla bla", timestamp: 75 },
      { id: 15, text: "Bla bla bla", timestamp: 115 },
    ];

    return {scenario, image, text};
  }
}
