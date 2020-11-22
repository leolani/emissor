import {Component, Input, OnInit} from '@angular/core';
import {Offset} from "../container";
import {ContainerComponent} from "../container/container.component";
import {TextSignal} from "../scenario";
import {Mention} from "../annotation";

@Component({
  templateUrl: './containers-text.component.html',
  styleUrls: ['./containers-text.component.css']
})
export class ContainersTextComponent implements OnInit, ContainerComponent<TextSignal, Offset> {
  @Input() data: TextSignal;
  @Input() selected: Offset;

  tokens: Mention<any>[];

  constructor() {}

  ngOnInit(): void {
    this.tokens = this.data.mentions.filter(mention =>
        mention.segment.container_id === this.data.id
        && mention.annotations.length
        && mention.annotations[0].type.toLowerCase() === "token");
  }

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
