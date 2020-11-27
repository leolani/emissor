import {Ruler} from "./representation/container";
import {ScenarioService} from "./scenario.service";
import {ContainerComponent} from "./container/container.component";
import {Type} from "@angular/core";
import {SegmentComponent} from "./segment/segment.component";
import {Annotation, Mention, Signal} from "./representation/scenario";
import {SegmentItem} from "./segment/segment-item";
import {AnnotationItem} from "./annotation/annotation-item";

function byId(obj) {
  return other => other.id === obj.id;
}

export class SignalSelection<S extends Signal<any>> {
  idx: number;
  signal: S;
  mention: Mention;
  segment: Ruler;
  annotation: Annotation<any>;

  containerComponent: Type<ContainerComponent<any>>;
  segmentItem: SegmentItem<any>;
  annotationItem: AnnotationItem<any>;

  private readonly scenarioId: string;
  private readonly scenarioService: ScenarioService;

  constructor(idx: number, signal: S, scenarioId: string, scenarioService: ScenarioService) {
    this.scenarioId = scenarioId;
    this.scenarioService = scenarioService;

    this.idx = idx;
    this.signal = signal;

    this.containerComponent = scenarioService.getContainerComponent(signal);
  }

  private clone() {
    let selection = new SignalSelection(this.idx, this.signal, this.scenarioId, this.scenarioService);
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

    selection.segmentItem = segment ?
        new SegmentItem<any>(this.scenarioService.getSegmentComponent(segment), segment) :
        null;

    return selection;
  }

  withAnnotation(annotation: Annotation<any>): SignalSelection<S> {
    let selection = this.clone();
    selection.mention = this.mention;
    selection.segment = this.segment;
    selection.annotation = annotation;

    selection.annotationItem = annotation ?
        new AnnotationItem<any>(this.scenarioService.getAnnotationComponent(annotation), annotation):
        null;

    return selection;
  }

  addMention(select = true): Promise<SignalSelection<S>> {
    let selection = this.clone();

    return this.scenarioService.getMentionFor(this.scenarioId, this.signal)
        .then(signal => {
          selection.signal = <S> signal;
          if (select) {
            selection = selection.withMention(signal.mentions.slice(-1)[0]);
          }

          return selection;
        });
  }

  addAnnotation(type: string, select = true): Promise<SignalSelection<S>> {
    let selection = this.clone();

    return this.scenarioService.getAnnotationFor(this.scenarioId, this.signal, this.mention, type)
        .then(signal => {
          selection.signal = <S> signal;
          if (select) {
            let newAnnotation = signal.mentions.find(byId(this.mention))
                .annotations.slice(-1)[0];
            selection = selection.withAnnotation(newAnnotation);
          }

          return selection;
        });
  }

  addSegment(type = null, select = true): Promise<SignalSelection<S>> {
    let selection = this.clone();

    return this.scenarioService.getSegmentFor(this.scenarioId, this.signal, this.mention, type)
        .then(signal => {
          selection.signal = <S> signal;
          if (select) {
            let newSegment = signal.mentions.find(byId(this.mention))
              .segment.slice(-1)[0];
            selection = selection.withSegment(newSegment);
          }

          return selection;
        });
  }

  getContainerComponent(): Type<ContainerComponent<any>> {
    return this.scenarioService.getContainerComponent(this.signal);
  }

  getSegmentComponent(): Type<SegmentComponent<any>> {
    return this.scenarioService.getSegmentComponent(this.segment);
  }

  getAnnotationComponent(): Type<SegmentComponent<any>> {
    return this.scenarioService.getSegmentComponent(this.segment);
  }
}
