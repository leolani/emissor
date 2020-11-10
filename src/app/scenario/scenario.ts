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
  timestamp: number;
}
