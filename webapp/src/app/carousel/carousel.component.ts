import {Component, Input, OnInit} from '@angular/core';
import {ImageSignal} from "../representation/scenario";
import {ScenarioService} from "../scenario.service";
import {SignalSelection} from "../signal-selection";
import {MultiIndex} from "../representation/container";

@Component({
  selector: 'app-carousel',
  templateUrl: './carousel.component.html',
  styleUrls: ['./carousel.component.css']
})
export class CarouselComponent implements OnInit {
  @Input() signals: ImageSignal[];
  @Input() selection: SignalSelection<ImageSignal>;

  constructor(private scenarioService: ScenarioService) { }

  ngOnInit(): void {}
}
