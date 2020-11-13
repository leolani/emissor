import {Ruler} from "./container";

export interface Mention {
  name: string;
  segment: Ruler;
  annotations: Annotation[];
}

export interface Annotation {
  name: string;
  type: string;
  value: string;
  src: string;
  timestamp: number;
}

export enum Emotion {
}

export interface Person {
  name: string;
}
