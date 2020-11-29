import { Type } from '@angular/core';
import {Ruler} from "../representation/container";

export class SegmentItem<T extends Ruler> {
  constructor(public component: Type<any>, public mentionId: string, public data: T) {}
}
