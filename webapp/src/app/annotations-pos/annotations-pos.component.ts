import {Component, Input, OnInit} from '@angular/core';
import {Annotation} from "../representation/scenario";

@Component({
  selector: 'app-annotations-pos',
  templateUrl: './annotations-pos.component.html',
  styleUrls: ['./annotations-pos.component.css']
})
export class AnnotationsPosComponent implements OnInit {
  @Input() data: Annotation<string>;

  constructor() { }

  ngOnInit(): void {
  }

}
