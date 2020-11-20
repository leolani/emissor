import {Component, Input, OnInit} from '@angular/core';
import {TimeRuler} from "../container";
import {AnnotationComponent} from "../annotation/annotation.component";

@Component({
  templateUrl: './annotations-display.component.html',
  styleUrls: ['./annotations-display.component.css']
})
export class AnnotationsDisplayComponent implements OnInit, AnnotationComponent<TimeRuler> {
  @Input() data: TimeRuler;

  constructor() { }

  ngOnInit(): void {
  }
}
