import {Component, Input, OnInit} from '@angular/core';
import {Scenario, Signal} from "../scenario";
import {ScenarioService} from "../scenario.service";
import {Options} from "@angular-slider/ngx-slider";
import {le as lowerBound} from "binary-search-bounds";


function compareByTimestamp(a: Signal, b: Signal): number {
  return a.timestamp - b.timestamp;
}


@Component({
  selector: 'app-modality',
  templateUrl: './modality.component.html',
  styleUrls: ['./modality.component.css']
})
export class ModalityComponent implements OnInit {
  @Input() scenario: Scenario;
  @Input() modality: string;

  sliderOptions: Options = {
    floor: 0,
    ceil: 1,
    showTicks: true,
  };

  signals: Signal[];
  selectedSignal: number = 0;

  constructor(private scenarioService: ScenarioService) { }

  ngOnInit(): void {
    this.loadSignals(this.modality);
  }

  loadSignals(modality: string): void {
    this.scenarioService.loadSignals(modality)
      .subscribe(signals => {
        this.signals = signals.sort(compareByTimestamp);
        this.setupSlider();
      });
  }

  setupSlider(): void {
    let timestamps = this.signals.map(signal => signal.timestamp)

    let options = Object.assign({}, this.sliderOptions);
    options.floor = 0;
    options.ceil = this.signals.length - 1;
    options.customValueToPosition = (val: number, minVal: number, maxVal: number): number => {
        return this.indexToTimlinePercentage(val, this.scenario, this.signals);
      };
    options.customPositionToValue = (percent: number, minVal: number, maxVal: number): number => {
        return this.timelinePercentageToIndex(percent, maxVal, minVal, this.scenario, timestamps);
      };

    this.selectedSignal = 0;
    this.sliderOptions = options;
  }

  private timelinePercentageToIndex(percent: number, maxVal: number, minVal: number, scenario: Scenario, timestamps: number[]) {
    let time: number = percent * (scenario.end - scenario.start) + scenario.start;
    let lowerIdx = lowerBound(timestamps, time);

    if (lowerIdx === timestamps.length - 1) {
      return timestamps.length - 1;
    }

    return time - timestamps[lowerIdx] <= timestamps[lowerIdx + 1] - time ? lowerIdx : lowerIdx + 1;
  }

  private indexToTimlinePercentage(val: number, scenario: Scenario, signals: Signal[]) {
    return (signals[val].timestamp - scenario.start)/(scenario.end -scenario.start);
  }

  onSignalSelect(idx: number): void {
    this.selectedSignal = idx;
  }
}
