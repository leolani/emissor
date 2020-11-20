import { Directive, ViewContainerRef } from '@angular/core';

@Directive({
  selector: '[segmentHost]',
})
export class AnnotationDirective {
  constructor(public viewContainerRef: ViewContainerRef) { }
}
