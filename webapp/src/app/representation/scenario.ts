import {
  ArrayContainer,
  Container,
  Index,
  MultiIndex,
  Ruler,
  Sequence,
  TemporalContainer,
  TemporalRuler
} from "./container";
import {Typed} from "./util";
import {Obj, Person} from "./entity";

export enum Modality {
  IMAGE, TEXT
}

export interface Annotation<T> extends Typed {
  value: T;
  source: string;
  timestamp: number;
}

export interface Mention {
  id: string;
  segment: Ruler[];
  annotations: Annotation<any>[];
  display?: string;
}


export interface Signal<R extends Ruler> extends Container<R> {
  modality: Modality;
  time: TemporalRuler;
  files: string[];
  mentions: Mention[];
  display?: string;
}


export interface TextSignal extends Signal<Index>, Sequence<string> {
  text: string
}

export interface ImageSignal extends Signal<MultiIndex>, ArrayContainer {
  image: string;
}


export interface ScenarioContext {
  agent: string;
  speaker: Person
  persons: Person[]
  objects: Obj[]
}


export interface Scenario extends TemporalContainer {
  context: ScenarioContext;
  signals: Record<string, string>;
}
