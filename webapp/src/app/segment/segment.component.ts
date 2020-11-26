import {Ruler} from "../representation/container";

export interface SegmentComponent<T extends Ruler> {
  data: T;
}
