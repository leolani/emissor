import {Injectable} from '@angular/core';
import {Observable} from 'rxjs';
import {Scenario, Signal} from "./scenario";

import {HttpClient} from '@angular/common/http';
import {map} from "rxjs/operators";

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
    let response = this.http.get<any[]>("/api/" + modality);
    switch (modality) {
      case "image":
        return response.pipe(
          map((signals: any[]) => signals.map(signal => {
            return {
              id: signal.id,
              name: signal.files.length && signal.files[0].replace(/^.*[\\\/]/, ''),
              image: signal.files.length && (this.resourcePath + "/" + scenarioName + "/" + signal.files[0]),
              time: signal.time,
              mentions: signal.mentions
            };
          }))
        );
      case "text":
        return response.pipe(
          map((signals: any[]) => signals.map(signal => {
            return {
              id: signal.id,
              name: signal.seq,
              text: signal.seq,
              time: signal.time,
              mentions: signal.mentions
            };
          }))
        );
      default:
        throw Error("Unknown modality: " + modality);
    }
  }
}
