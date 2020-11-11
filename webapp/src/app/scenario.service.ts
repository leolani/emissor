import {Injectable} from '@angular/core';
import {Observable} from 'rxjs';
import {Scenario, Signal} from "./scenario";

import {HttpClient, HttpParams} from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class ScenarioService {
  private scenarioEndpoint = "'api/scenario"
  private modalityEndpoint = "'api/"

  constructor(private http: HttpClient) { }

  loadScenario(scenarioPath: string): Observable<Scenario> {
    const params = new HttpParams()
      .set('path', "1");
      // .set('path', scenarioPath);

    return this.http.get<Scenario>(this.scenarioEndpoint + "/1")//, {params})
  }

  loadSignals(modalityPath: string): Observable<Signal[]> {
    return this.http.get<Signal[]>(this.modalityEndpoint + modalityPath)
  }
}
