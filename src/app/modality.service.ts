import {Injectable} from '@angular/core';
import {Observable} from 'rxjs';

import {HttpClient} from '@angular/common/http';
import {Signal} from "./modality";

@Injectable({
  providedIn: 'root'
})
export class ModalityService {

  private modalityEndpoint = "'api/signals"

  constructor(private http: HttpClient) { }

  loadSignals(): Observable<Signal[]> {
    return this.http.get<Signal[]>(this.modalityEndpoint)
  }
}
