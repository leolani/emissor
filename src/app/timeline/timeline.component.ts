import {Component, OnInit} from '@angular/core';
import {ModalityService} from '../modality.service';
import {Signal} from "../modality";

@Component({
  selector: 'app-timeline',
  templateUrl: './timeline.component.html',
  styleUrls: ['./timeline.component.css']
})
export class TimelineComponent implements OnInit {

  signals: Signal[];
  selectedSignal: Signal;

  constructor(private modalityService: ModalityService) { }

  ngOnInit(): void {
    this.loadSignals()
  }

  loadSignals() {
    this.modalityService.loadSignals()
      .subscribe(signals => this.signals = signals);
  }

  onSelect(signal: Signal): void {
    this.selectedSignal = signal;
  }
}
