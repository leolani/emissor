import {Component, Input, OnInit, Output, EventEmitter} from '@angular/core';
import {ScenarioService} from "../scenario.service";
import {SignalSelection} from "../signal-selection";
import {Annotation, Mention} from "../representation/scenario";
import {ComponentService} from "../component.service";

@Component({
  selector: 'app-editor',
  templateUrl: './editor.component.html',
  styleUrls: ['./editor.component.css']
})
export class EditorComponent implements OnInit {
  // TODO rename to selection
  @Input() signal: SignalSelection<any>;
  @Output() signalChange = new EventEmitter<SignalSelection<any>>();

  annotationType: string;

  constructor(private scenarioService: ScenarioService, private componentService: ComponentService) { }

  ngOnInit(): void {}

  addMention() {
    this.signal.addMention().then(selection => {
      this.signal = selection;
      this.signalChange.emit(this.signal);
    });
  }

  addAnnotation() {
    this.signal.addAnnotation(this.annotationType).then(selection => {
      this.signal = selection;
      this.signalChange.emit(this.signal);
    });
  }

  addSegment() {
    let type = null;
    switch (this.signal.signal.type.toLowerCase()) {
      case "imagesignal":
        type = "multiindex";
        break;
      case "textsignal":
        type = "index";
        break;
      default:
        // pass
    }

    this.signal.addSegment(type).then(selection => {
      this.signal = selection;
      this.signalChange.emit(this.signal);
    });
  }

  selectMention(mentionId: string) {
    let mention = this.signal.signal.mentions.find(mention => mention.id === mentionId);

    let changedSignal = this.signal.withMention(mention);
    if (mention && mention.segment.length) {
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
    this.signalChange.emit(this.signal);
  }

  getAnnotationTypes(): string[] {
    return this.componentService.getAnnotationTypes();
  }
}
