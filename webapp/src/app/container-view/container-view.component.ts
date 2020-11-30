import {
  AfterViewInit,
  Component,
  ComponentFactoryResolver, EventEmitter,
  Input,
  OnChanges,
  OnInit,
  Output,
  SimpleChanges,
  ViewChild
} from '@angular/core';
import {ContainerDirective} from "../container/container.directive";
import {ContainerComponent} from "../container/container.component";
import {SignalSelection} from "../signal-selection";
import {observableToBeFn} from "rxjs/internal/testing/TestScheduler";

@Component({
  selector: 'app-container-view',
  templateUrl: './container-view.component.html',
  styleUrls: ['./container-view.component.css']
})
export class ContainerViewComponent implements OnInit, OnChanges {
  @Input() selection: SignalSelection<any>;
  @Output() selectionChange = new EventEmitter<SignalSelection<any>>();

  @ViewChild(ContainerDirective, {static: true}) containerHost: ContainerDirective;

  constructor(private componentFactoryResolver: ComponentFactoryResolver) { }

  ngOnInit() {
    this.selection.containerComponent && this.loadComponent(this.selection);
  }

  ngOnChanges(changes: SimpleChanges) {
    changes.selection
        && changes.selection.currentValue.containerComponent
        && this.loadComponent(changes.selection.currentValue);
  }

  private loadComponent(selection: SignalSelection<any>) {
    const componentFactory = this.componentFactoryResolver.resolveComponentFactory(selection.containerComponent);

    const viewContainerRef = this.containerHost.viewContainerRef;
    viewContainerRef.clear();

    const componentRef = viewContainerRef.createComponent<ContainerComponent<any>>(componentFactory);
    componentRef.instance.selection = selection;
    componentRef.instance.selectionChange.subscribe(event => this.selectionChange.emit(event));
  }
}
