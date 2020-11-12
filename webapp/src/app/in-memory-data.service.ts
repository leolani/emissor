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
      { id: 11, name: 'Dr Nice', time: {start: 0, end: 0}, image: "assets/testimages/maxima.jpg"},
      { id: 12, name: 'Narco', time: {start: 1, end: 1}, image: "assets/testimages/piek-sunglasses.jpg" },
      { id: 13, name: 'Bombasto', time: {start: 2, end: 2}, image: "assets/testimages/soccer-balll.png" },
      { id: 14, name: 'Celeritas', time: {start: 10, end: 10}, image: "assets/testimages/niqee-2020-10-25 at 17.30.51.png" },
      { id: 15, name: 'Magneta', time: {start: 12, end: 12}, image: "assets/testimages/maxima.jpg" },
      { id: 16, name: 'RubberMan', time: {start: 22, end: 22}, image: "assets/testimages/soccer-balll.png" },
      { id: 17, name: 'Dynama', time: {start: 34, end: 34}, image: "assets/testimages/piek-sunglasses.jpg" },
      { id: 18, name: 'Dr IQ', time: null, image: "assets/testimages/sam-2020-10-25 at 17.30.25.png" },
      { id: 19, name: 'Magma', time: {start: 100, end: 100}, image: "assets/testimages/piek-sunglasses.jpg" },
      { id: 20, name: 'Tornado', time: {start: 101, end: 101}, image: "assets/testimages/soccer-balll.png" }
    ];

    const text = [
      { id: 11, name: "One", text: "Bla bla bla", time: {start: 15, end: 25}},
      { id: 13, name: "Two", text: "Bla bla bla", time: {start: 45, end: 70} },
      { id: 12, name: "Three", text: "Bla bla bla", time: null},
      { id: 14, name: "Four", text: "Bla bla bla", time: {start: 75, end: 100}},
      { id: 15, name: "Five", text: "Bla bla bla", time: null},
    ];

    return {scenario, image, text};
  }
}
