import { Directive, ViewContainerRef } from '@angular/core';

@Directive({
  selector: '[segmentHost]',
})
export class SegmentDirective {
  constructor(public viewContainerRef: ViewContainerRef) { }
}
