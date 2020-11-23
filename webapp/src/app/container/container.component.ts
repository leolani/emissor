import {Ruler} from "../container";
import {SignalSelection} from "../signal-selection";

// TODO Remove ContainerItem
// TODO Remove data (= signal)
export interface ContainerComponent<T, R extends Ruler> {
  data: T;
  selection: SignalSelection;
}
