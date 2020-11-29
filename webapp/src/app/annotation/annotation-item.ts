import { Type } from '@angular/core';
import {AnnotationComponent} from "./annotation.component";

export class AnnotationItem<T> {
  constructor(public component: Type<AnnotationComponent<T>>, public mentionId: string, public data: T) {}
}
