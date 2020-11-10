import {Injectable} from '@angular/core';
import {Observable} from 'rxjs';

import {HttpClient} from '@angular/common/http';
import {Scenario, Signal} from "./scenario";

@Injectable({
  providedIn: 'root'
})
export class ScenarioService {

  private scenarioEndpoint = "'api/scenario"
  private modalityEndpoint = "'api/"

  constructor(private http: HttpClient) { }

  listScenarios(): Observable<Scenario[]> {
    return this.http.get<Scenario[]>(this.scenarioEndpoint)
  }

  loadSignals(modality: string): Observable<Signal[]> {
    return this.http.get<Signal[]>(this.modalityEndpoint + modality)
  }
}
