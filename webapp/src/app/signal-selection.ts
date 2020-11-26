import {Ruler} from "./representation/container";
import {ScenarioService} from "./scenario.service";
import {ContainerComponent} from "./container/container.component";
import {Type} from "@angular/core";
import {SegmentComponent} from "./segment/segment.component";
import {Annotation, Mention, Signal} from "./representation/scenario";
import {SegmentItem} from "./segment/segment-item";
import {AnnotationItem} from "./annotation/annotation-item";

export class SignalSelection<S extends Signal<any>> {
  idx: number;
  signal: S;
  mention: Mention;
  segment: Ruler;
  annotation: Annotation<any>;

  containerComponent: Type<ContainerComponent<any>>;
  segmentItem: SegmentItem<any>;
  annotationItem: AnnotationItem<any>;

  private readonly scenarioService: ScenarioService;

  constructor(idx: number, signal: S, scenarioService: ScenarioService) {
    this.scenarioService = scenarioService;

    this.idx = idx;
    this.signal = signal;

    this.containerComponent = scenarioService.getContainerComponent(signal);
  }

  private clone() {
    let selection = new SignalSelection(this.idx, this.signal, this.scenarioService);
    selection.mention = this.mention;
    selection.segment = this.segment;
    selection.annotation = this.annotation;
    selection.containerComponent = this.containerComponent;
    selection.segmentItem = this.segmentItem;
    selection.annotationItem = this.annotationItem;

    return selection;
  }

  withMention(mention: Mention): SignalSelection<S> {
    let selection = this.clone();
    selection.mention = mention;
    selection.segment = null;
    selection.annotation = null;

    return selection;
  }

  withSegment(segment: Ruler): SignalSelection<S> {
    let selection = this.clone();
    selection.mention = this.mention;
    selection.segment = segment;
    selection.annotation = this.annotation;

    selection.segmentItem = new SegmentItem<any>(this.scenarioService.getSegmentComponent(segment), segment);

    return selection;
  }

  withAnnotation(annotation: Annotation<any>): SignalSelection<S> {
    let selection = this.clone();
    selection.mention = this.mention;
    selection.segment = this.segment;
    selection.annotation = annotation;

    selection.annotationItem = new AnnotationItem<any>(this.scenarioService.getAnnotationComponent(annotation), annotation);

    return selection;
  }

  addMention(select = true): SignalSelection<S> {
    let selection = this.clone();
    let newMention = this.scenarioService.getMentionFor(selection.signal);
    selection.signal.mentions.push(newMention);

    if (select) {
      selection = selection.withMention(newMention);
    }

    return selection;
  }

  addAnnotation(type, select = true): SignalSelection<S> {
    let selection = this.clone();

    let newAnnotation = this.scenarioService.getAnnotationFor(type, selection.signal);
    selection.mention.annotations.push(newAnnotation);

    if (select) {
      selection = selection.withAnnotation(newAnnotation);
    }

    return selection;
  }

  addSegment(type = null, select = true): SignalSelection<S> {
    let selection = this.clone();

    let mention = selection.mention;
    let previous = mention.segment.length && mention.segment.slice(-1)[0];

    let newSegment: any;
    if (type) {
      throw Error();
    } else if (previous) {
      newSegment = JSON.parse(JSON.stringify(previous));
    } else {
      newSegment = this.scenarioService.getSegmentFor(selection.signal)
    }

    mention.segment.push(newSegment);
    if (select) {
      selection = selection.withSegment(newSegment);
    }

    return selection;
  }

  getContainerComponent(): Type<ContainerComponent<any>> {
    return this.scenarioService.getContainerComponent(this.signal);
  }

  getSegemntComponent(): Type<SegmentComponent<any>> {
    return this.scenarioService.getSegmentComponent(this.segment);
  }

  getAnnotationComponent(): Type<SegmentComponent<any>> {
    return this.scenarioService.getSegmentComponent(this.segment);
  }
}
