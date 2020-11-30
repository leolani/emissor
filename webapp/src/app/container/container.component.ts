import {Ruler} from "../representation/container";
import {SignalSelection} from "../signal-selection";
import {Signal} from "../representation/scenario";
import {EventEmitter, Output} from "@angular/core";

export interface ContainerComponent<S extends Signal<any>> {
  selection: SignalSelection<S>;
  selectionChange: EventEmitter<SignalSelection<any>>;
}
