import {Injectable, Type} from '@angular/core';
import {Observable} from 'rxjs';
import {Annotation, ImageSignal, Mention, Scenario, Signal, TextSignal} from "./representation/scenario";

import {HttpClient, HttpHeaders, HttpParams} from '@angular/common/http';
import {map} from "rxjs/operators";
import {SegmentsTimeComponent} from "./segments-time/segments-time.component";
import {SegmentsBoundingboxComponent} from "./segments-boundingbox/segments-boundingbox.component";
import {AnnotationComponent} from "./annotation/annotation.component";
import {AnnotationsDisplayComponent} from "./annotations-display/annotations-display.component";
import {SegmentComponent} from "./segment/segment.component";
import {Ruler} from "./representation/container";
import {ContainersImgComponent} from "./containers-img/containers-img.component";
import {ContainersTextComponent} from "./containers-text/containers-text.component";
import {ContainerComponent} from "./container/container.component";
import {SegmentsOffsetComponent} from "./segments-offset/segments-offset.component";
import {SegmentsAtomicComponent} from "./segments-atomic/segments-atomic.component";


@Injectable({
  providedIn: 'root'
})
export class ComponentService {

  constructor() { }

  getAnnotationComponent(annotation: Annotation<any>): Type<AnnotationComponent<any>> {
    switch (annotation.type.toLowerCase()) {
      case "display":
        return AnnotationsDisplayComponent
      case "token":
        return AnnotationsDisplayComponent
      default:
        throw Error("Unsupported annotation type: " + annotation.type);
    }
  }

  getSegmentComponent(ruler: Ruler): Type<SegmentComponent<any>> {
    switch (ruler.type.toLowerCase()) {
      case "multiindex":
        return SegmentsBoundingboxComponent
      case "temporalruler":
        return SegmentsTimeComponent
      case "index":
        return SegmentsOffsetComponent
      case "atomicruler":
        return SegmentsAtomicComponent
      default:
        throw Error("Unsupported segment type: " + ruler.type);
    }
  }

  getContainerComponent(selectedSignal: Signal<any> | Annotation<any>): Type<ContainerComponent<any>> {
    switch (selectedSignal.type.toLowerCase()) {
      case "textsignal":
        return ContainersTextComponent
      case "imagesignal":
        return ContainersImgComponent
      default:
        throw Error("Unsupported container type: " + selectedSignal.type);
    }
  }
}

