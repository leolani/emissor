import {Component, Input, OnInit} from '@angular/core';
import {TimeRuler} from "../container";
import {AnnotationComponent} from "../annotation/annotation.component";

@Component({
  templateUrl: './annotations-label.component.html',
  styleUrls: ['./annotations-label.component.css']
})
export class AnnotationsLabelComponent implements OnInit, AnnotationComponent<TimeRuler> {
  @Input() data: TimeRuler;

  constructor() { }

  ngOnInit(): void {
  }
}
