import {Component, Input, OnInit} from '@angular/core';
import {Signal} from "../scenario";
import {ScenarioService} from "../scenario.service";
import {ContainerItem} from "../container/container-item";


@Component({
  selector: 'app-text-view',
  templateUrl: './text-view.component.html',
  styleUrls: ['./text-view.component.css']
})
export class TextViewComponent implements OnInit {
  @Input() signals: Signal[];
  @Input() selected: Signal;

  containerItem: ContainerItem<any, any>;

  constructor(private scenarioService: ScenarioService) {}

  ngOnInit(): void {}

  ngOnChanges(changes) {
    let selected = (changes.selected && changes.selected.currentValue) || this.selected || 0;
    let container = this.scenarioService.getContainerComponent(this.signals[selected]);
    this.containerItem = new ContainerItem(container, this.signals[selected], null);
  }
}
