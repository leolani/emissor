import {Ruler} from "../container";
import {Mention} from "../annotation";

export interface SegmentComponent<T extends Ruler> {
  data: T;
}
