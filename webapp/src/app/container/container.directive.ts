import { Directive, ViewContainerRef } from '@angular/core';

@Directive({
  selector: '[containerHost]',
})
export class ContainerDirective {
  constructor(public viewContainerRef: ViewContainerRef) { }
}
