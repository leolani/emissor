import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {Annotation, ImageSignal, Mention} from "../representation/scenario";
import {SignalSelection} from "../signal-selection";
import {SegmentItem} from "../segment/segment-item";
import {AnnotationItem} from "../annotation/annotation-item";
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

  selectMention(mention: Mention, $event: MouseEvent) {
    let selection = this.selection.withMention(mention);
    if (mention.segment.length) {
      selection = selection.withSegment(mention.segment[0]);
    }
    this.selection = selection
    $event.stopPropagation();
    this.selectionChange.emit(this.selection);
  }

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

  save() {
    this.scenarioService.saveSignal(this.selection.scenarioId, this.selection.signal);
  }

  annotationDisplayValue(annotation: AnnotationItem<any>) {
    return annotationDisplayValue(annotation.data);
  }


  segmentDisplayValue(segment: Ruler) {
    return (segment && segmentDisplayValue(segment)) || "";
  }
}

import {ScenarioService} from "../scenario.service";
import {annotationDisplayValue}  from "../representation/annotation";

import {Ruler, segmentDisplayValue} from "../representation/container";
