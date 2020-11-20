import {Component, Input, OnInit} from '@angular/core';
import {SegmentComponent} from "../segment/segment.component";
import {BoundingBox} from "../container";

@Component({
  templateUrl: './segments-boundingbox.component.html',
  styleUrls: ['./segments-boundingbox.component.css']
})
export class SegmentsBoundingboxComponent implements OnInit, SegmentComponent<BoundingBox> {
  @Input() data: BoundingBox;

  constructor() { }

  ngOnInit(): void {
  }
}
