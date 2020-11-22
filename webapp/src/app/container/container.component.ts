import {Ruler} from "../container";
import {SignalSelection} from "../signal-selection";

export interface ContainerComponent<T, R extends Ruler> {
  data: T;
  selection: SignalSelection;
}
