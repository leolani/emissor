import { Type } from '@angular/core';
import {Ruler} from "../representation/container";
import {ContainerComponent} from "./container.component";
import {SignalSelection} from "../signal-selection";

export class ContainerItem<T, R extends Ruler> {
  constructor(public component: Type<ContainerComponent<T, R>>, public data: any, public selection: SignalSelection) {}
}
