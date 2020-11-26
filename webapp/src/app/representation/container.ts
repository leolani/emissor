import {Typed} from "./util";

export interface Ruler extends Typed {
  container_id: string;
  display?: string;
}

export interface Container<R extends Ruler> extends Typed {
  id: string;
  ruler: R;
}

export interface Index extends Ruler {
  start: number;
  stop: number;
}

export interface Sequence<T> extends Container<Index> {
  seq: T[];
}

export interface MultiIndex extends Ruler {
  bounds: [number, number, number, number];
}

export interface ArrayContainer extends Container<MultiIndex> {
  array: number[][];
}

export interface TemporalRuler extends Ruler {
  start: number;
  end: number;
}

export interface TemporalContainer extends Container<TemporalRuler> {
  // no content
}

export interface AtomicRuler extends Ruler {
  // no content
}

export interface AtomicContainer<T> extends Container<AtomicRuler> {
  value: T;
}
