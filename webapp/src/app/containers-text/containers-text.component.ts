import {Component, Input, OnInit} from '@angular/core';
import {Offset} from "../container";
import {ContainerComponent} from "../container/container.component";
import {TextSignal} from "../scenario";
import {Mention} from "../annotation";
import {SignalSelection} from "../signal-selection";

@Component({
  templateUrl: './containers-text.component.html',
  styleUrls: ['./containers-text.component.css']
})
export class ContainersTextComponent implements OnInit, ContainerComponent<TextSignal, Offset> {
  @Input() data: TextSignal;
  @Input() selection: SignalSelection;

  tokens: Mention<any>[];

  constructor() {}

  ngOnInit(): void {
    this.tokens = this.data.mentions.filter(mention =>
        mention.segment.length === 1
        && mention.segment[0].container_id === this.data.id
        && mention.annotations.length
        && mention.annotations[0].type.toLowerCase() === "token");
  }

  characterClass(idx: number) {
    // if (this.selection.segment && (<Offset> this.selection.segment).contains(idx)) {
    //   return "selected";
    // }
    //
    // if (this.data.mentions.flatMap(men => men.segment).some(seg => seg.contains(idx))) {
    //   return "mentioned";
    // }

    return "plain";
  }

  counter(range: number) {
    return Array.from(Array(range).keys());
  }

  tokenClass(idx: number) {
    if (this.selection.segment && (<Offset> this.selection.segment).contains(idx)) {
      return "selected";
    }
  }
}
