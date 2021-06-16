import {Injectable} from '@angular/core';
import {Observable} from 'rxjs';
import {Annotation, ImageSignal, Mention, Scenario, Signal, TextSignal} from "./representation/scenario";

import {HttpClient, HttpHeaders, HttpParams} from '@angular/common/http';
import {map} from "rxjs/operators";
import {Ruler} from "./representation/container";


@Injectable({
  providedIn: 'root'
})
export class ScenarioService {
  // private scenarioEndpoint = "/api/scenario"
  private scenarioEndpoint = 'http://localhost:5000/api/scenario';
  private resourcePath = 'http://localhost:5000/data';

  constructor(private http: HttpClient) { }

  listScenarios(): Observable<string[]> {
    return this.http.get<string[]>(this.scenarioEndpoint);
  }

  loadScenario(scenarioName: string): Observable<Scenario> {
    return this.http.get<Scenario>(this.scenarioEndpoint + "/" + scenarioName);
  }

  loadSignals(scenarioName, modality: string): Observable<Signal<any>[]> {
    // return this.http.get<any[]>("/api/" + modality).pipe(
    return this.http.get<Signal<any>[]>(this.scenarioEndpoint + "/" + scenarioName + "/" + modality).pipe(
      map((signals: any[]) => signals.map(signal =>
        this.setSignalValue(scenarioName, signal, this.resourcePath)))
    );
  }

  saveSignal(scenario: string, signal: Signal<any>) {
    this.http.post(this.scenarioEndpoint + '/' + scenario + '/' + signal['@type'] + '/' + signal.id,
      JSON.stringify(signal), this.getJSONHeaders()).subscribe();
  }

  setSignalValue(scenarioName: string, signal: Signal<any>, basePath: string) {
    console.log(signal['@type']);
    switch (signal['@type'].toLowerCase()) {
      case 'imagesignal':
        let fileName = signal.files.length && signal.files[0].replace(/^.*[\\\/]/, '');
        (<ImageSignal> signal).image = signal.files.length && (basePath + '/' + scenarioName + '/' + signal.files[0]);
        signal.display = signal.display || fileName;
        break;
      case 'textsignal':
        (<TextSignal> signal).text = (<TextSignal> signal).seq.join('');
        signal.display = signal.display || (<TextSignal> signal).text;
        break;
      default:
        throw Error("Unknown signal type: " + signal['@type']);
    }

    this.setDisplayValue(signal);

    return signal;
  }

  setDisplayValue(signal: Signal<any>): void {
    signal.mentions.forEach(mention => {
      mention.display = this.getMentionDisplayValue(mention);
      mention.segment.forEach(seg => seg.display = mention.display);
    });
    let displayAnnotations = signal.mentions.flatMap(mention => mention.annotations)
        .filter(ann => ann.type.toLowerCase() === "display")
        .sort((a, b) => a.timestamp - b.timestamp);
    signal.display = (displayAnnotations.length && displayAnnotations[0].value) || signal.display || signal.id;
  }

  getMentionDisplayValue(mention: Mention) {
    let displayAnnotations = mention.annotations
      .filter(ann => ann.type === "display")
      .sort((a, b) => b.timestamp - a.timestamp);

    return displayAnnotations.length && displayAnnotations[0].value;
  }

  createMentionFor(scenarioId: string, signal: Signal<any>): Promise<Mention> {
    let path = `/${scenarioId}/${signal.modality}/${signal.id}/mention`

    return this.http.put<Mention>(this.scenarioEndpoint + path, null).toPromise();
  }

  createAnnotationFor(scenarioId: string, signal: Signal<any>, mention: Mention, type: string): Promise<Annotation<any>> {
    let path = `/${scenarioId}/${signal.modality}/${signal.id}/${mention.id}/annotation`

    let params = new HttpParams();
    params = params.append('type', type);

    return this.http.put<Annotation<any>>(this.scenarioEndpoint + path, null, {params}).toPromise();
  }

  createSegmentFor(scenarioId: string, signal: Signal<any>, mention: Mention, type: string,
                containerId: string = null): Promise<Ruler> {
    let path = `/${scenarioId}/${signal.modality}/${signal.id}/${mention.id}/segment`

    let params = new HttpParams();
    params = params.append('type', type);
    if (containerId) {
      params = params.append('container', containerId);
    }

    return this.http.put<Ruler>(this.scenarioEndpoint + path, null, {params}).toPromise();
  }

  private getJSONHeaders(): any {
    let headers = new HttpHeaders({
      'Content-Type': 'application/json'
    });

    return {headers};
  }
}

