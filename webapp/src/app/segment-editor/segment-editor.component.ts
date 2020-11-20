import {Component, ComponentFactoryResolver, Input, OnChanges, OnInit, SimpleChanges, ViewChild} from '@angular/core';
import {SegmentItem} from "../segment/segment-item";
import {SegmentDirective} from "../segment/segment.directive";
import {SegmentComponent} from "../segment/segment.component";

@Component({
  selector: 'app-segment-editor',
  templateUrl: './segment-editor.component.html',
  styleUrls: ['./segment-editor.component.css']
})
export class SegmentEditorComponent implements OnInit, OnChanges {
  @Input() segment: SegmentItem<any>;

  @ViewChild(SegmentDirective, {static: true}) segmentHost: SegmentDirective;

  constructor(private componentFactoryResolver: ComponentFactoryResolver) { }

  ngOnInit() {
    this.segment && this.loadComponent(this.segment);
  }

  ngOnChanges(changes: SimpleChanges) {
    changes.segment.currentValue
        && changes.segment.currentValue != changes.segment.previousValue
        && this.loadComponent(changes.segment.currentValue);
  }

  private loadComponent(segmentItem: SegmentItem<any>) {
    const componentFactory = this.componentFactoryResolver.resolveComponentFactory(segmentItem.component);

    const viewContainerRef = this.segmentHost.viewContainerRef;
    viewContainerRef.clear();

    const componentRef = viewContainerRef.createComponent<SegmentComponent<any>>(componentFactory);
    componentRef.instance.data = segmentItem.data;
  }
}
