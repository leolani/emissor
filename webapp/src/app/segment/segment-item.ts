import { Type } from '@angular/core';
import {Ruler} from "../container";
import {Mention} from "../annotation";

export class SegmentItem<T extends Ruler> {
  constructor(public component: Type<any>, public data: T) {}
}
