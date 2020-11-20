import {Ruler} from "./container";
import {Type} from "@angular/core";

export class Mention<T extends Ruler> {
  id: string;
  segment: T;
  component: Type<any>;
  display: string;
  annotations: Annotation<any>[];

  constructor(id: string, display: string, segment: T, component: Type<any>, annotations: Annotation<any>[]) {
    this.id = id;
    this.segment = segment;
    this.component = component;
    this.display = display;
    this.annotations = annotations;
  }
}

export class Annotation<T> {
  type: string;
  value: T;
  src: string;
  timestamp: number;

  constructor(name: string, type: string, value: T, src: string, timestamp: number) {
    this.type = type;
    this.value = value;
    this.src = src;
    this.timestamp = timestamp;
  }
}

export enum Emotion {
}

export class Person {
  name: string;

  constructor(name: string) {
    this.name = name;
  }
}
