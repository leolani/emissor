import {Ruler} from "../container";

export interface ContainerComponent<T, R extends Ruler> {
  data: T;
  selected: R;
}
