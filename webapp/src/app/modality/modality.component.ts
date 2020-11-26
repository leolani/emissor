import {Component, Input, OnInit} from '@angular/core';
import {Scenario, Signal} from "../scenario";
import {ScenarioService} from "../scenario.service";
import {Options} from "@angular-slider/ngx-slider";
import {le as lowerBound} from "binary-search-bounds";
import {DomSanitizer, SafeUrl} from "@angular/platform-browser";
import {SignalSelection} from "../signal-selection";


function compareByTimestamp(a: Signal<any>, b: Signal<any>): number {
  if (a.time && b.time) {
    return a.time.start - b.time.start;
  }

  return a.time ? 1 : -1;
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

  rangeOptions: Options = {
    floor: 0,
    ceil: 1,
    draggableRange: true,
    pushRange: true,
    readOnly: true
  };

  signals: Signal<any>[];
  signalEntries: Array<[number, Signal<any>]>;
  selectedSignal: number = 0;
  editSignal: boolean = false;

  selection: SignalSelection;

  constructor(private scenarioService: ScenarioService, private sanitizer: DomSanitizer) { }

  ngOnInit(): void {
    this.loadSignals(this.modality);
  }

  onSliderSelection(idx: number) {
    this.selection = new SignalSelection(idx, this.signals[idx], this.scenarioService);
  }

  loadSignals(modality: string): void {
    this.scenarioService.loadSignals(this.scenario.id, modality)
      .subscribe(signals => {
        this.signals = signals.sort(compareByTimestamp);
        this.signalEntries = Array.from(this.signals.entries());
        this.setupSlider();
        this.setupRange();
      });
  }

  setupSlider(): void {
    let timestamps = this.signals.map(signal => signal.time.start)

    let options = Object.assign({}, this.sliderOptions);
    options.floor = 0;
    options.ceil = this.signals.length - 1;
    options.customValueToPosition = (val: number, minVal: number, maxVal: number): number => {
      return this.indexToTimelinePercentage(val, this.scenario, this.signals);
    };
    options.customPositionToValue = (percent: number, minVal: number, maxVal: number): number => {
      return this.timelinePercentageToIndex(percent, maxVal, minVal, this.scenario, timestamps);
    };

    this.selectedSignal = 0;
    this.sliderOptions = options;
    this.onSliderSelection(0);
  }

  setupRange(): void {
    let rangeOptions = Object.assign({}, this.rangeOptions);
    rangeOptions.floor = this.scenario.ruler.start;
    rangeOptions.ceil = this.scenario.ruler.end;

    this.rangeOptions = rangeOptions;
  }

  private timelinePercentageToIndex(percent: number, maxVal: number, minVal: number, scenario: Scenario, timestamps: number[]): number {
    let time: number = percent * (scenario.ruler.end - scenario.ruler.start) + scenario.ruler.start;
    let lowerIdx = lowerBound(timestamps, time);

    if (lowerIdx === timestamps.length - 1) {
      return timestamps.length - 1;
    }

    return time - timestamps[lowerIdx] <= timestamps[lowerIdx + 1] - time ? lowerIdx : lowerIdx + 1;
  }

  private indexToTimelinePercentage(val: number, scenario: Scenario, signals: Signal<any>[]): number {
    return (signals[val].time.start - scenario.ruler.start)/(scenario.ruler.end -scenario.ruler.start);
  }

  onSignalSelect(idx: number): void {
    if (!this.editSignal) {
      this.selectedSignal = idx;
    }
  }

  toggleEdit(): void {
    this.editSignal = !this.editSignal;

    let rangeOptions = Object.assign({}, this.rangeOptions);
    rangeOptions.readOnly = !this.editSignal;
    this.rangeOptions = rangeOptions;

    let sliderOptions = Object.assign({}, this.sliderOptions);
    sliderOptions.readOnly = this.editSignal;
    this.sliderOptions = sliderOptions;

    if (!this.editSignal) {
      // let selectedId = this.signals[this.selectedSignal].id
      // TODO reset selection
      this.signals = this.signals.sort(compareByTimestamp);
      this.setupSlider();
    }
  }

  getDataUri(): SafeUrl {
    const jsonData = JSON.stringify(this.signals);
    const uri = 'data:application/json;charset=UTF-8,' + encodeURIComponent(jsonData);

    return this.sanitizer.bypassSecurityTrustUrl(uri);
  }

  save() {
    this.scenarioService.saveSignal(this.scenario.id, this.selection.signal);
  }

}
