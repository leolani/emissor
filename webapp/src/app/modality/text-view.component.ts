import {Component, Input, OnInit} from '@angular/core';
import {Signal} from "../scenario";
import {ScenarioService} from "../scenario.service";
import {ContainerItem} from "../container/container-item";
import {SignalSelection} from "../signal-selection";


@Component({
  selector: 'app-text-view',
  templateUrl: './text-view.component.html',
  styleUrls: ['./text-view.component.css']
})
export class TextViewComponent implements OnInit {
  @Input() signals: Signal[];
  @Input() selection: SignalSelection;

  constructor(private scenarioService: ScenarioService) {}

  ngOnInit(): void {}
}
