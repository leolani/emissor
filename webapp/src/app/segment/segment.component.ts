import {Ruler} from "../container";

export interface SegmentComponent<T extends Ruler> {
  data: T;
}
