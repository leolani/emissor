import {Component, Input, OnInit} from '@angular/core';
import {SegmentComponent} from "../segment/segment.component";
import {Index} from "../representation/container";

@Component({
  templateUrl: './segments-atomic.component.html',
  styleUrls: ['./segments-atomic.component.css']
})
export class SegmentsAtomicComponent implements OnInit, SegmentComponent<Index> {
  @Input() data: Index;

  constructor() { }

  ngOnInit(): void {
  }
}
