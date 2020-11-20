import {Component, Input, OnChanges, OnInit, SimpleChanges} from '@angular/core';
import {Signal} from "../scenario";
import {Annotation, Mention} from "../annotation";
import {SegmentItem} from "../segment/segment-item";

@Component({
  selector: 'app-annotation',
  templateUrl: './annotation.component.html',
  styleUrls: ['./annotation.component.css']
})
export class AnnotationComponent implements OnInit, OnChanges {
  @Input() signal: Signal;

  selectedMention: Mention<any>;
  selectedAnnotation: Annotation<any>;
  segmentItem: SegmentItem<any>;

  constructor() { }

  ngOnInit(): void {
    // this.selectedMention = this.signal.mentions.length && this.signal.mentions[0]
    // this.selectedAnnotation = this.selectedMention && this.selectedMention.annotations.length
    //                           && this.selectedMention.annotations[0]
  }

  ngOnChanges(changes: SimpleChanges) {
    console.log(changes);
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
    this.segmentItem = mention && new SegmentItem(mention.component, mention.segment);
  }

  selectAnnotation(annotation: Annotation<any>) {
    this.selectedAnnotation = annotation;
  }
}
