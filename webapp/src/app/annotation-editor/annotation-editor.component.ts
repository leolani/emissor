import {Component, ComponentFactoryResolver, Input, OnChanges, OnInit, SimpleChanges, ViewChild} from '@angular/core';
import {AnnotationItem} from "../annotation/annotation-item";
import {AnnotationDirective} from "../annotation/annotation.directive";
import {AnnotationComponent} from "../annotation/annotation.component";

@Component({
  selector: 'app-annotation-editor',
  templateUrl: './annotation-editor.component.html',
  styleUrls: ['./annotation-editor.component.css']
})
export class AnnotationEditorComponent implements OnInit, OnChanges {
  @Input() annotation: AnnotationItem<any>;

  @ViewChild(AnnotationDirective, {static: true}) annotationHost: AnnotationDirective;

  constructor(private componentFactoryResolver: ComponentFactoryResolver) { }

  ngOnInit() {
    this.annotation && this.loadComponent(this.annotation);
  }

  ngOnChanges(changes: SimpleChanges) {
    changes.annotation.currentValue
        && changes.annotation.currentValue != changes.annotation.previousValue
        && this.loadComponent(changes.annotation.currentValue);
  }

  private loadComponent(annotationItem: AnnotationItem<any>) {
    const componentFactory = this.componentFactoryResolver.resolveComponentFactory(annotationItem.component);

    const viewContainerRef = this.annotationHost.viewContainerRef;
    viewContainerRef.clear();

    const componentRef = viewContainerRef.createComponent<AnnotationComponent<any>>(componentFactory);
    componentRef.instance.data = annotationItem.data;
  }
}
