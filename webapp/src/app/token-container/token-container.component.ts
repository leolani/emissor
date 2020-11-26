import {Component, Input, OnInit} from '@angular/core';
import {Index} from "../representation/container";

@Component({
  selector: 'app-token-container',
  templateUrl: './token-container.component.html',
  styleUrls: ['./token-container.component.css']
})
export class TokenContainerComponent implements OnInit {
  @Input() containerId: string;
  @Input() tokens: string[];
  @Input() segments: Index[];
  @Input() selected: Index;

  constructor() {}

  ngOnInit(): void {
  }

  tokenClass(idx: number) {
    if (this.selected && this.selected.start <= idx && idx < this.selected.stop) {
      return "selected";
    }

    if (this.segments.some(seg => seg.start <= idx && idx < seg.stop)) {
      return "mentioned";
    }

    return "plain";
  }

  counter(range: number) {
    return Array.from(Array(range).keys());
  }
}
