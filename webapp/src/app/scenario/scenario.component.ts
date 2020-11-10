import {Component, OnInit} from '@angular/core';
import {ScenarioService} from './scenario.service';
import {Scenario, Signal} from "./scenario";

@Component({
  selector: 'app-scenario',
  templateUrl: './scenario.component.html',
  styleUrls: ['./scenario.component.css']
})
export class ScenarioComponent implements OnInit {

  scenarios: Scenario[];
  selectedScenario: Scenario;

  signals: Signal[];
  selectedSignal: Signal;

  constructor(private scenarioService: ScenarioService) { }

  ngOnInit(): void {
    this.listScenarios();
  }

  listScenarios(): void {
    this.scenarioService.listScenarios()
      .subscribe(scenarios => this.scenarios = scenarios);
  }

  loadSignals(modality: string): void {
    this.scenarioService.loadSignals(modality)
      .subscribe(signals => this.signals = signals);
  }

  onScenarioSelect(scenario: Scenario) {
    this.selectedScenario = scenario;
  }

  onSignalSelect(signal: Signal): void {
    this.selectedSignal = signal;
  }
}
