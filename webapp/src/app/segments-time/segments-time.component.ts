import {Component, Input, OnInit} from '@angular/core';
import {SegmentComponent} from "../segment/segment.component";
import {TimeRuler} from "../container";

@Component({
  templateUrl: './segments-time.component.html',
  styleUrls: ['./segments-time.component.css']
})
export class SegmentsTimeComponent implements OnInit, SegmentComponent<TimeRuler> {
  @Input() data: TimeRuler;

  constructor() { }

  ngOnInit(): void {
  }
}
