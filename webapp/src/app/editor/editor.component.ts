import {Component, Input, OnInit, Output, EventEmitter} from '@angular/core';
import {Annotation, Mention} from "../annotation";
import {ScenarioService} from "../scenario.service";
import {SignalSelection} from "../signal-selection";

@Component({
  selector: 'app-editor',
  templateUrl: './editor.component.html',
  styleUrls: ['./editor.component.css']
})
export class EditorComponent implements OnInit {
  @Input() signal: SignalSelection;
  @Output() signalChange = new EventEmitter<SignalSelection>();;

  // selectedMention: Mention<any>;
  // selectedAnnotation: Annotation<any>;
  // segmentItem: SegmentItem<any>;
  // annotationItem: AnnotationItem<any>;

  constructor(private scenarioService: ScenarioService) { }

  ngOnInit(): void {}

  // ngOnChanges(changes: SimpleChanges) {
  //   if (changes.signal.previousValue !== changes.signal.currentValue) {
  //     this.selectedMention = null;
  //     this.selectedAnnotation = null;
  //   }
  // }

  addAnnotation() {
    let mention = this.signal.mention;
    let len = mention.annotations.length;
    let previous = len && mention.annotations[len - 1];
    mention.annotations.push({
      src: (previous && previous.src) || "",
      timestamp: new Date().getTime(),
      value: "",
      type: (previous && previous.type) || ""
    });
  }

  addSegment() {
    let mention = this.signal.mention;
    let len = mention.segment.length;
    let previous = len && mention.segment[len - 1];
    mention.segment.push(previous && JSON.parse(JSON.stringify(previous)));
  }

  selectMention(mention: Mention<any>) {
    let changedSignal = this.signal.withMention(mention);
    if (mention.segment.length) {
      changedSignal = changedSignal.withSegment(changedSignal.mention.segment[0]);
    }
    this.signal = changedSignal;
    this.signalChange.emit(changedSignal);
  }

  selectSegment(segment: any) {
    this.signal = this.signal.withSegment(segment);
    this.signalChange.emit(this.signal);
  }

  selectAnnotation(annotation: Annotation<any>) {
    this.signal = this.signal.withAnnotation(annotation);
    console.log("anntotation", annotation, this.signal);
    this.signalChange.emit(this.signal);
  }
}
