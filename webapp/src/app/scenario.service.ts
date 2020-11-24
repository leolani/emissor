import {Injectable, Type} from '@angular/core';
import {Observable} from 'rxjs';
import {ImageSignal, Scenario, Signal, TextSignal} from "./scenario";

import {HttpClient, HttpHeaders} from '@angular/common/http';
import {map} from "rxjs/operators";
import {Annotation, Mention} from "./annotation";
import {SegmentsTimeComponent} from "./segments-time/segments-time.component";
import {SegmentsBoundingboxComponent} from "./segments-boundingbox/segments-boundingbox.component";
import {AnnotationComponent} from "./annotation/annotation.component";
import {AnnotationsDisplayComponent} from "./annotations-display/annotations-display.component";
import {SegmentComponent} from "./segment/segment.component";
import {BoundingBox, Offset, Ruler} from "./container";
import {ContainersImgComponent} from "./containers-img/containers-img.component";
import {ContainersTextComponent} from "./containers-text/containers-text.component";
import {ContainerComponent} from "./container/container.component";


@Injectable({
  providedIn: 'root'
})
export class ScenarioService {
  // private scenarioEndpoint = "/api/scenario"
  private scenarioEndpoint = "https://localhost:5000/api/scenario"
  private resourcePath = "/assets"

  constructor(private http: HttpClient) { }

  listScenarios(): Observable<string[]> {
    return this.http.get<string[]>(this.scenarioEndpoint);
  }

  loadScenario(scenarioName: string): Observable<Scenario> {
    return this.http.get<Scenario>(this.scenarioEndpoint + "/" + scenarioName)
  }

  loadSignals(scenarioName, modality: string): Observable<Signal[]> {
    // return this.http.get<any[]>("/api/" + modality).pipe(
    return this.http.get<Signal[]>(this.scenarioEndpoint + "/" + scenarioName + "/" + modality).pipe(
      map((signals: any[]) => signals.map(signal =>
        this.convertSignal(scenarioName, modality, signal, this.resourcePath)))
    );
  }

  saveSignal(scenario: string, signal :Signal) {
    this.http.post(this.scenarioEndpoint + "/" + scenario + "/" + signal.type + "/" + signal.id,
      JSON.stringify(signal), this.getJSONHeaders()).subscribe();
  }

  convertSignal(scenarioName: string, modality: string, signal: any, basePath: string) {
    switch (modality) {
      case "image":
        let fileName = signal.files.length && signal.files[0].replace(/^.*[\\\/]/, '');
        let imagePath = signal.files.length && (basePath + "/" + scenarioName + "/" + signal.files[0]);
        let imageMentions = signal.mentions.map(this.convertMention);

        return new ImageSignal(signal.id, signal.type, fileName, signal.time, imageMentions, imagePath);
      case "text":
        let textMentions = signal.mentions.map(this.convertMention);
        let text = signal.seq.join('');
        return new TextSignal(signal.id, signal.type, text, signal.time, textMentions, text);
      default:
        throw Error("Unknown modality: " + modality);
    }
  }

  convertMention(mention: any, idx: number): Mention<any> {
    let displayAnnotations = mention.annotations.filter(ann => ann.type.toLowerCase() === "display")
      .sort((a, b) => a.timestamp - b.timestamp);
    let display = (displayAnnotations.length && displayAnnotations[0].value) || mention.id || idx;
    let segment = mention.segment;

    return new Mention(mention.id, display, segment, mention.annotations);
  }

  getAnnotationComponent(annotation: Annotation<any>): Type<AnnotationComponent<any>> {
    switch (annotation.type.toLowerCase()) {
      case "display":
        return AnnotationsDisplayComponent
      default:
        throw Error("Unsupported annotation type: " + annotation.type);
    }
  }

  getSegmentComponent(ruler: Ruler): Type<SegmentComponent<any>> {
    switch (ruler.type.toLowerCase()) {
      case "bbox":
        return SegmentsBoundingboxComponent
      case "temporalruler":
        return SegmentsTimeComponent
      default:
        throw Error("Unsupported segment type: " + ruler.type);
    }
  }

  getContainerComponent(selectedSignal: Signal | Annotation<any>): Type<ContainerComponent<any, any>> {
    switch (selectedSignal.constructor.name) {
      case TextSignal.name:
        return ContainersTextComponent
      case ImageSignal.name:
        return ContainersImgComponent
      default:
        throw Error("Unsupported container type: " + selectedSignal.constructor.name);
    }
  }

  getMentionFor(signal: Signal): Mention<any> {
    return new Mention<any>("", "new", [], [
      new Annotation<any>("new", "display", "new", "", new Date().getTime())]);
  }

  getAnnotationFor(type: string, signal: Signal): Annotation<any> {
    switch (type.toLowerCase()) {
      case "display":
        return new Annotation<string>("new", "display", "new", "", new Date().getTime());
      default:
        throw Error("Unsupported type: " + signal.type);
    }
  }

  getSegmentFor(signal: Signal): Ruler {
    switch (signal.type.toLowerCase()) {
      case "imagesignal":
        return new BoundingBox("new", 0,0,0,0);
      case "textsignal":
        return new Offset(0, 0);
      default:
        throw Error("Unsupported type: " + signal.type);
    }
  }

  private getJSONHeaders(): any {
    let headers = new HttpHeaders({
      'Content-Type': 'application/json'
    });

    return {headers};
  }
}

