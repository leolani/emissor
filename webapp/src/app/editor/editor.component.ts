import {Component, Input, OnChanges, OnInit, SimpleChanges} from '@angular/core';
import {Signal} from "../scenario";
import {Annotation, Mention} from "../annotation";
import {SegmentItem} from "../segment/segment-item";
import {AnnotationItem} from "../annotation/annotation-item";
import {ScenarioService} from "../scenario.service";

@Component({
  selector: 'app-editor',
  templateUrl: './editor.component.html',
  styleUrls: ['./editor.component.css']
})
export class EditorComponent implements OnInit, OnChanges {
  @Input() signal: Signal;

  selectedMention: Mention<any>;
  selectedAnnotation: Annotation<any>;
  segmentItem: SegmentItem<any>;
  annotationItem: AnnotationItem<any>;

  constructor(private scenarioService: ScenarioService) { }

  ngOnInit(): void {}

  ngOnChanges(changes: SimpleChanges) {
    if (changes.signal.previousValue !== changes.signal.currentValue) {
      this.selectedMention = null;
      this.selectedAnnotation = null;
    }
  }

  addAnnotation() {
    let len = this.selectedMention.annotations.length;
    let previous = len && this.selectedMention.annotations[len - 1];
    this.selectedMention.annotations.push({
      src: (previous && previous.src) || "",
      timestamp: new Date().getTime(),
      value: "",
      type: (previous && previous.type) || ""
    });
  }

  selectMention(mention: Mention<any>) {
    this.selectedMention = mention;
    let component = this.scenarioService.getSegmentComponent(mention.segment);
    this.segmentItem = mention && new SegmentItem(component, mention.segment);
  }

  selectAnnotation(annotation: Annotation<any>) {
    this.selectedAnnotation = annotation;
    let component = this.scenarioService.getAnnotationComponent(annotation);
    this.annotationItem = annotation && new AnnotationItem(component, annotation);
  }
}
