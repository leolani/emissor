import {Ruler} from "../container";
import {Mention} from "../annotation";

export interface AnnotationComponent<T extends Ruler> {
  data: T;
}
