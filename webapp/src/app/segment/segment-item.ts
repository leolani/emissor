import { Type } from '@angular/core';
import {Ruler} from "../container";

export class SegmentItem<T extends Ruler> {
  constructor(public component: Type<any>, public data: T) {}
}
