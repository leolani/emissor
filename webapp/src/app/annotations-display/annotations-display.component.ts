import {Component, Input, OnInit} from '@angular/core';
import {AnnotationComponent} from "../annotation/annotation.component";
import {Annotation} from "../annotation";

@Component({
  templateUrl: './annotations-display.component.html',
  styleUrls: ['./annotations-display.component.css']
})
export class AnnotationsDisplayComponent implements OnInit, AnnotationComponent<string> {
  @Input() data: Annotation<string>;

  constructor() { }

  ngOnInit(): void {
  }
}
