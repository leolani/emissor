import {Component, Input, OnInit} from '@angular/core';
import {Offset} from "../container";
import {ContainerComponent} from "../container/container.component";
import {TextSignal} from "../scenario";

@Component({
  templateUrl: './containers-text.component.html',
  styleUrls: ['./containers-text.component.css']
})
export class ContainersTextComponent implements OnInit, ContainerComponent<TextSignal, Offset> {
  @Input() data: TextSignal;
  @Input() selected: Offset;

  constructor() {}

  ngOnInit(): void {}

  characterClass(idx: number) {
    if (this.selected && this.selected.contains(idx)) {
      return "selected";
    }

    if (this.data.mentions.some(mention => mention.segment.contains(idx))) {
      return "mentioned";
    }

    return "plain";
  }

  counter(range: number) {
    return Array.from(Array(range).keys());
  }
}
