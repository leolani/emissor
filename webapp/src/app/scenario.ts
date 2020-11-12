export interface Scenario {
  id: number;
  name: string;
  start: number;
  end: number;
  modalities: Map<string, string>;
}

export interface Signal {
  id: number;
  name: string;
  time: TimeRuler;
}

export interface ImageSignal extends Signal {
  image: string;
}

export interface TextSignal extends Signal {
  text: string;
}

export interface TimeRuler {
  start: number;
  end: number;
}
