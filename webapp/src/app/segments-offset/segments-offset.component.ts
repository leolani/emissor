import {Component, Input, OnInit} from '@angular/core';
import {SegmentComponent} from "../segment/segment.component";
import {Index} from "../representation/container";

@Component({
  templateUrl: './segments-offset.component.html',
  styleUrls: ['./segments-offset.component.css']
})
export class SegmentsOffsetComponent implements OnInit, SegmentComponent<Index> {
  @Input() data: Index;

  constructor() { }

  ngOnInit(): void {
  }
}
