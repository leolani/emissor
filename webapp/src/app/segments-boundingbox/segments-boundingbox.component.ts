import {Component, Input, OnInit} from '@angular/core';
import {SegmentComponent} from "../segment/segment.component";
import {MultiIndex} from "../representation/container";

@Component({
  templateUrl: './segments-boundingbox.component.html',
  styleUrls: ['./segments-boundingbox.component.css']
})
export class SegmentsBoundingboxComponent implements OnInit, SegmentComponent<MultiIndex> {
  @Input() data: MultiIndex;

  constructor() { }

  ngOnInit(): void {
  }
}
