import {Ruler} from "../representation/container";
import {SignalSelection} from "../signal-selection";
import {Signal} from "../representation/scenario";

export interface ContainerComponent<S extends Signal<any>> {
  selection: SignalSelection<S>;
}
