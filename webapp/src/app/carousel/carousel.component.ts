import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {Annotation, ImageSignal} from "../representation/scenario";
import {SignalSelection} from "../signal-selection";
import {SegmentItem} from "../segment/segment-item";
import {AnnotationItem} from "../annotation/annotation-item";
import {ScenarioService} from "../scenario.service";

import {annotationDisplayValue}  from "../representation/annotation";
import {segmentDisplayValue}  from "../representation/container";

@Component({
  selector: 'app-carousel',
  templateUrl: './carousel.component.html',
  styleUrls: ['./carousel.component.css']
})
export class CarouselComponent implements OnInit {
  @Input() signals: ImageSignal[];
  @Input() selection: SignalSelection<ImageSignal>;
  @Output() selectionChange = new EventEmitter<SignalSelection<any>>();

  annotationType: string;

  constructor(private scenarioService: ScenarioService) { }

  ngOnInit(): void {}

  selectSegment(segment: SegmentItem<any>, $event: MouseEvent) {
    this.selection = this.selection.withSegment(segment.data, segment.mentionId);
    $event.stopPropagation();
    this.selectionChange.emit(this.selection);
  }

  selectAnnotation(annotation: AnnotationItem<any>, $event: MouseEvent) {
    this.selection = this.selection.withAnnotation(annotation.data, annotation.mentionId);
    $event.stopPropagation();
    this.selectionChange.emit(this.selection);
  }

  addMention() {
    this.selection.addMention().then(selection => {
      this.selection = selection;
      this.selectionChange.emit(this.selection);
    });
  }

  addAnnotation() {
    this.selection.addAnnotation(this.annotationType).then(selection => {
      this.selection = selection;
      this.selectionChange.emit(this.selection);
    });
  }

  save() {
    this.scenarioService.saveSignal(this.selection.scenarioId, this.selection.signal);
  }

  annotationDisplayValue(annotation: AnnotationItem<any>) {
    return annotationDisplayValue(annotation.data);
  }

  segmentDisplayValue(segment: SegmentItem<any>) {
    return segmentDisplayValue(segment.data);
  }
}
