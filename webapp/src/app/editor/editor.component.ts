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

  selectMention(mention: Mention<any>) {
    this.signal = this.signal.withMention(mention).withSegment(mention.segment);
    this.signalChange.emit(this.signal);
  }

  selectAnnotation(annotation: Annotation<any>) {
    this.signal = this.signal.withAnnotation(annotation);
    this.signalChange.emit(this.signal);
  }
}
