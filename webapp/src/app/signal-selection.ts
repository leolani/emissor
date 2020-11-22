import {Ruler} from "./container";
import {Annotation, Mention} from "./annotation";
import {ScenarioService} from "./scenario.service";
import {ContainerComponent} from "./container/container.component";
import {Type} from "@angular/core";
import {SegmentComponent} from "./segment/segment.component";
import {ContainerItem} from "./container/container-item";
import {Signal} from "./scenario";
import {SegmentItem} from "./segment/segment-item";
import {AnnotationItem} from "./annotation/annotation-item";

export class SignalSelection {
  idx: number;
  signal: Signal;
  mention: Mention<any>;
  segment: Ruler;
  annotation: Annotation<any>;

  containerItem: ContainerItem<any, any>;
  segmentItem: SegmentItem<any>;
  annotationItem: AnnotationItem<any>;

  private readonly scenarioService: ScenarioService;

  constructor(idx: number, signal: Signal, scenarioService: ScenarioService) {
    this.scenarioService = scenarioService;

    this.idx = idx;
    this.signal = signal;

    this.containerItem = new ContainerItem<any, any>(scenarioService.getContainerComponent(signal),
        signal, this);
  }

  withMention(mention: Mention<any>): SignalSelection {
    let selection = new SignalSelection(this.idx, this.signal, this.scenarioService);
    selection.mention = mention;
    selection.segment = null;
    selection.annotation = null;

    return selection;
  }

  withSegment(segment: Ruler): SignalSelection {
    let selection = new SignalSelection(this.idx, this.signal, this.scenarioService);
    selection.mention = this.mention;
    selection.segment = segment;
    selection.annotation = this.annotation;

    selection.segmentItem = new SegmentItem<any>(this.scenarioService.getSegmentComponent(segment), segment);

    return selection;
  }

  withAnnotation(annotation: Annotation<any>): SignalSelection {
    let selection = new SignalSelection(this.idx, this.signal, this.scenarioService);
    selection.mention = this.mention;
    selection.segment = this.segment;
    selection.annotation = annotation;

    selection.annotationItem = new AnnotationItem<any>(this.scenarioService.getAnnotationComponent(annotation), annotation);

    return selection;
  }

  getContainerComponent(): Type<ContainerComponent<any, any>> {
    return this.scenarioService.getContainerComponent(this.signal);
  }

  getSegemntComponent(): Type<SegmentComponent<any>> {
    return this.scenarioService.getSegmentComponent(this.segment);
  }

  getAnnotationComponent(): Type<SegmentComponent<any>> {
    return this.scenarioService.getSegmentComponent(this.segment);
  }
}

