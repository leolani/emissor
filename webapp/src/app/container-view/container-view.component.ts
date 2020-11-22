import {Component, ComponentFactoryResolver, Input, OnChanges, OnInit, SimpleChanges, ViewChild} from '@angular/core';
import {ContainerDirective} from "../container/container.directive";
import {ContainerComponent} from "../container/container.component";
import {ContainerItem} from "../container/container-item";

@Component({
  selector: 'app-container-view',
  templateUrl: './container-view.component.html',
  styleUrls: ['./container-view.component.css']
})
export class ContainerViewComponent implements OnInit, OnChanges {
  @Input() container: ContainerItem<any, any>;

  @ViewChild(ContainerDirective, {static: true}) containerHost: ContainerDirective;

  constructor(private componentFactoryResolver: ComponentFactoryResolver) { }

  ngOnInit() {
    this.container && this.loadComponent(this.container);
  }

  ngOnChanges(changes: SimpleChanges) {
    changes.container.currentValue
        && changes.container.currentValue != changes.container.previousValue
        && this.loadComponent(changes.container.currentValue);
  }

  private loadComponent(containerItem: ContainerItem<any, any>) {
    const componentFactory = this.componentFactoryResolver.resolveComponentFactory(containerItem.component);

    const viewContainerRef = this.containerHost.viewContainerRef;
    viewContainerRef.clear();

    const componentRef = viewContainerRef.createComponent<ContainerComponent<any, any>>(componentFactory);
    componentRef.instance.data = containerItem.data;
    componentRef.instance.selection = containerItem.selection;
  }
}
