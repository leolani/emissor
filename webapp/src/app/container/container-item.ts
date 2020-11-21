import { Type } from '@angular/core';
import {Ruler} from "../container";
import {ContainerComponent} from "./container.component";

export class ContainerItem<T, R extends Ruler> {
  constructor(public component: Type<ContainerComponent<T, R>>, public data: any, public selected: R) {}
}
