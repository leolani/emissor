import {Component, Input, OnInit} from '@angular/core';
import {Index} from "../representation/container";
import {ContainerComponent} from "../container/container.component";
import {Mention, TextSignal} from "../representation/scenario";
import {SignalSelection} from "../signal-selection";

@Component({
  templateUrl: './containers-text.component.html',
  styleUrls: ['./containers-text.component.css']
})
export class ContainersTextComponent implements OnInit, ContainerComponent<TextSignal, Index> {
  @Input() data: TextSignal;
  @Input() selection: SignalSelection;

  tokens: Mention[];

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
    if (this.selection.segment && this.contains((<Index> this.selection.segment), idx)) {
      return "selected";
    }
  }

  private contains(segment: Index, idx: number) {
    return segment.start < idx && idx < segment.stop;
  }
}
