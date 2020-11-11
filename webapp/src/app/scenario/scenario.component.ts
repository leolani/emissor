import {Component, OnInit} from '@angular/core';
import {ScenarioService} from './scenario.service';
import {Scenario, Signal} from "./scenario";

@Component({
  selector: 'app-scenario',
  templateUrl: './scenario.component.html',
  styleUrls: ['./scenario.component.css']
})
export class ScenarioComponent implements OnInit {
  scenarioPath: string;
  scenario: Scenario;

  signals: Signal[];
  selectedSignal: Signal;

  constructor(private scenarioService: ScenarioService) { }

  ngOnInit(): void {}

  loadScenario(): void {
    this.scenarioService.loadScenario(this.scenarioPath)
      .subscribe(scenario => this.scenario = scenario);
  }

  loadSignals(modality: string): void {
    this.scenarioService.loadSignals(modality)
      .subscribe(signals => this.signals = signals);
  }

  onSignalSelect(signal: Signal): void {
    this.selectedSignal = signal;
  }
}
