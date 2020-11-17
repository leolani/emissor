import {Ruler, TimeRuler} from "./container";
import {Annotation, Mention} from "./annotation";

export interface Scenario {
  id: string;
  name: string;
  start: number;
  end: number;
  signals: Map<string, string>;
}

export interface Signal {
  id: number;
  name: string;
  time: TimeRuler;
  mentions: Mention[];
}

export interface ImageSignal extends Signal {
  image: string;
}

export interface TextSignal extends Signal {
  text: string;
}
