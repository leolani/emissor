import {Component, Input, OnInit} from '@angular/core';
import {Offset} from "../container";

@Component({
  selector: 'app-text-container',
  templateUrl: './text-container.component.html',
  styleUrls: ['./text-container.component.css']
})
export class TextContainerComponent implements OnInit {
  @Input() containerId: string;
  @Input() text: string;
  @Input() segments: Offset[];
  @Input() selected: Offset;

  constructor() {}

  ngOnInit(): void {
  }

  characterClass(idx: number) {
    if (this.selected && this.selected.contains(idx)) {
      return "selected";
    }

    if (this.segments.some(seg => seg.contains(idx))) {
      return "mentioned";
    }

    return "plain";
  }

  counter(range: number) {
    return Array.from(Array(range).keys());
  }
}
