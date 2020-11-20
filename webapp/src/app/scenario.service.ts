import {Injectable} from '@angular/core';
import {Observable} from 'rxjs';
import {ImageSignal, Scenario, Signal, TextSignal} from "./scenario";

import {HttpClient} from '@angular/common/http';
import {map} from "rxjs/operators";
import {Mention} from "./annotation";
import {BoundingBox} from "./container";
import {BoundingboxComponent} from "./boundingbox/boundingbox.component";
import {SegmentsTimeComponent} from "./segments-time/segments-time.component";
import {SegmentsBoundingboxComponent} from "./segments-boundingbox/segments-boundingbox.component";

@Injectable({
  providedIn: 'root'
})
export class ScenarioService {
  private scenarioEndpoint = "/api/scenario"
  private resourcePath = "/assets"

  constructor(private http: HttpClient) { }

  listScenarios(): Observable<string[]> {
    return this.http.get<Scenario[]>(this.scenarioEndpoint).pipe(
      map((scenarios: Scenario[]) => scenarios.map(scenario => scenario.id))
    );
  }

  loadScenario(scenarioName: string): Observable<Scenario> {
    return this.http.get<Scenario>(this.scenarioEndpoint + "/" + scenarioName)
  }

  loadSignals(scenarioName, modality: string): Observable<Signal[]> {
    // return this.http.get<Signal[]>(this.scenarioEndpoint + "/" + scenarioName + "/" + modality)
    return this.http.get<any[]>("/api/" + modality).pipe(
      map((signals: any[]) => signals.map(signal =>
        this.convertSignal(scenarioName, modality, signal, this.resourcePath)))
    );
  }

  convertSignal(scenarioName: string, modality: string, signal: any, basePath: string) {
    switch (modality) {
      case "image":
        let fileName = signal.files.length && signal.files[0].replace(/^.*[\\\/]/, '');
        let imagePath = signal.files.length && (basePath + "/" + scenarioName + "/" + signal.files[0]);
        let imageMentions = signal.mentions.map(this.convertMention);

        return new ImageSignal(signal.id, fileName, signal.time, imageMentions, imagePath);
      case "text":
        let textMentions = signal.mentions.map(this.convertMention);
        return new TextSignal(signal.id, signal.seq, signal.time, textMentions, signal.seq);
      default:
        throw Error("Unknown modality: " + modality);
    }
  }

  convertMention(mention: any): Mention<any> {
    let displayAnnotations = mention.annotations.filter(ann => ann.type.toLowerCase() === "display")
      .sort((a, b) => a.timestamp - b.timestamp);
    let display = (displayAnnotations.length && displayAnnotations[0].value) || mention.id;
    let segment = mention.segment;
    let component;
    switch (segment.type) {
      case "MultiIndex":
        component = SegmentsBoundingboxComponent
        break;
      case "TemporalRuler":
        component = SegmentsTimeComponent
        break;
      default:
        throw Error("Unsupported segment type: " + segment.type);
    }

    return new Mention(mention.id, display, segment, component, mention.annotations);
  }
}

