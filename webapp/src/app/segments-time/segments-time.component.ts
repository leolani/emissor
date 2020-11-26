import {Component, Input, OnInit} from '@angular/core';
import {SegmentComponent} from "../segment/segment.component";
import {TemporalRuler} from "../representation/container";

@Component({
  templateUrl: './segments-time.component.html',
  styleUrls: ['./segments-time.component.css']
})
export class SegmentsTimeComponent implements OnInit, SegmentComponent<TemporalRuler> {
  @Input() data: TemporalRuler;

  constructor() { }

  ngOnInit(): void {
  }
}
