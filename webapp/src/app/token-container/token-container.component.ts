import {Component, Input, OnInit} from '@angular/core';
import {Offset} from "../container";

@Component({
  selector: 'app-token-container',
  templateUrl: './token-container.component.html',
  styleUrls: ['./token-container.component.css']
})
export class TokenContainerComponent implements OnInit {
  @Input() containerId: string;
  @Input() tokens: string[];
  @Input() segments: Offset[];
  @Input() selected: Offset;

  constructor() {}

  ngOnInit(): void {
  }

  tokenClass(idx: number) {
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
