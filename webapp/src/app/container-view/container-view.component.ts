import {Component, ComponentFactoryResolver, Input, OnChanges, OnInit, SimpleChanges, ViewChild} from '@angular/core';
import {ContainerDirective} from "../container/container.directive";
import {ContainerComponent} from "../container/container.component";
import {ContainerItem} from "../container/container-item";
import {SignalSelection} from "../signal-selection";

@Component({
  selector: 'app-container-view',
  templateUrl: './container-view.component.html',
  styleUrls: ['./container-view.component.css']
})
export class ContainerViewComponent implements OnInit, OnChanges {
  @Input() selection: SignalSelection;

  @ViewChild(ContainerDirective, {static: true}) containerHost: ContainerDirective;

  constructor(private componentFactoryResolver: ComponentFactoryResolver) { }

  ngOnInit() {
    this.selection.containerItem && this.loadComponent(this.selection);
  }

  ngOnChanges(changes: SimpleChanges) {
    changes.selection
        && changes.selection.currentValue.containerItem
        && this.loadComponent(changes.selection.currentValue);
  }

  private loadComponent(selection: SignalSelection) {
    const componentFactory = this.componentFactoryResolver.resolveComponentFactory(selection.containerItem.component);

    const viewContainerRef = this.containerHost.viewContainerRef;
    viewContainerRef.clear();

    const componentRef = viewContainerRef.createComponent<ContainerComponent<any, any>>(componentFactory);
    componentRef.instance.data = selection.signal;
    componentRef.instance.selection = selection;
  }
}
