import {Component, Input, OnInit} from '@angular/core';
import {ImageSignal} from "../representation/scenario";
import {ContainerItem} from "../container/container-item";
import {ScenarioService} from "../scenario.service";
import {SignalSelection} from "../signal-selection";

@Component({
  selector: 'app-carousel',
  templateUrl: './carousel.component.html',
  styleUrls: ['./carousel.component.css']
})
export class CarouselComponent implements OnInit {
  @Input() signals: ImageSignal[];
  @Input() selection: SignalSelection;

  containerItem: ContainerItem<any, any>;

  constructor(private scenarioService: ScenarioService) { }

  ngOnInit(): void {}
}
