import {Injectable, Type} from '@angular/core';
import {Observable} from 'rxjs';
import {Annotation, ImageSignal, Mention, Scenario, Signal, TextSignal} from "./representation/scenario";

import {HttpClient, HttpHeaders} from '@angular/common/http';
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

  loadSignals(scenarioName, modality: string): Observable<Signal<any>[]> {
    // return this.http.get<any[]>("/api/" + modality).pipe(
    return this.http.get<Signal<any>[]>(this.scenarioEndpoint + "/" + scenarioName + "/" + modality).pipe(
      map((signals: any[]) => signals.map(signal =>
        this.setSignalValue(scenarioName, signal, this.resourcePath)))
    );
  }

  saveSignal(scenario: string, signal :Signal<any>) {
    this.http.post(this.scenarioEndpoint + "/" + scenario + "/" + signal.type + "/" + signal.id,
      JSON.stringify(signal), this.getJSONHeaders()).subscribe();
  }

  setSignalValue(scenarioName: string, signal: Signal<any>, basePath: string) {
    switch (signal.type.toLowerCase()) {
      case "imagesignal":
        let fileName = signal.files.length && signal.files[0].replace(/^.*[\\\/]/, '');
        (<ImageSignal> signal).image = signal.files.length && (basePath + "/" + scenarioName + "/" + signal.files[0]);
        signal.display = signal.display || fileName;
        break;
      case "textsignal":
        (<TextSignal> signal).text = (<TextSignal> signal).seq.join('');
        signal.display = signal.display || (<TextSignal> signal).text;
        break;
      default:
        throw Error("Unknown signal type: " + signal.type);
    }

    this.setDisplayValue(signal);

    return signal;
  }

  setDisplayValue(signal: Signal<any>): void {
    let displayAnnotations = signal.mentions.flatMap(mention => mention.annotations)
        .filter(ann => ann.type.toLowerCase() === "display")
        .sort((a, b) => a.timestamp - b.timestamp);
    signal.display = (displayAnnotations.length && displayAnnotations[0].value) || signal.display || signal.id;
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
      case "multiindex":
        return SegmentsBoundingboxComponent
      case "temporalruler":
        return SegmentsTimeComponent
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

  getMentionFor(signal: Signal<any>): Mention {
    // return new Mention("", "new", [], [
    //   new Annotation<any>("new", "display", "new", "", new Date().getTime())]);
    return null;
  }

  getAnnotationFor(type: string, signal: Signal<any>): Annotation<any> {
    // switch (type.toLowerCase()) {
    //   case "display":
    //     return new Annotation<string>("new", "display", "new", "", new Date().getTime());
    //   default:
    //     throw Error("Unsupported type: " + signal.type);
    // }
    return null;
  }

  getSegmentFor(signal: Signal<any>): Ruler {
    // switch (signal.type.toLowerCase()) {
    //   case "imagesignal":
    //     return new BoundingBox("new", 0,0,0,0);
    //   case "textsignal":
    //     return new Offset(0, 0);
    //   default:
    //     throw Error("Unsupported type: " + signal.type);
    // }
    return null;
  }

  private getJSONHeaders(): any {
    let headers = new HttpHeaders({
      'Content-Type': 'application/json'
    });

    return {headers};
  }
}

