import {Component, OnInit} from '@angular/core';
import {ScenarioService} from '../scenario.service';
import {Scenario, Signal} from "../scenario";

@Component({
  selector: 'app-scenario',
  templateUrl: './scenario.component.html',
  styleUrls: ['./scenario.component.css']
})
export class ScenarioComponent implements OnInit {
  scenarioPath: string;
  scenario: Scenario;

  constructor(private scenarioService: ScenarioService) { }

  ngOnInit(): void {}

  loadScenario(): void {
    this.scenarioService.loadScenario(this.scenarioPath)
      .subscribe(scenario => this.scenario = scenario);
  }
}
