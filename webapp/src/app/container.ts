export interface Ruler {
  type: string;
}

export class Offset implements Ruler {
  type: string = "offset";
  start: number;
  end:number;

  constructor(start: number, end: number) {
    this.start = start;
    this.end = end;
  }

  contains(idx: number): boolean {
    return this.start <= idx && idx < this.end;
  }
}

export class BoundingBox implements Ruler {
  type: string = "bbox";
  label: string;
  bounds: number[];

  constructor(label: string, x_min: number, y_min: number, x_max: number, y_max: number) {
    this. label = label;
    this.bounds = [x_min, y_min, x_max, y_max];
  }
}

export class TimeRuler implements Ruler {
  type: string = "time";
  start: number;
  end: number;

  constructor(start: number, end: number) {
    this.start = start;
    this.end = end;
  }
}
