import { Directive, ViewContainerRef } from '@angular/core';

@Directive({
  selector: '[annotationHost]',
})
export class AnnotationDirective {
  constructor(public viewContainerRef: ViewContainerRef) { }
}
