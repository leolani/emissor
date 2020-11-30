import {Component, Input, OnInit} from '@angular/core';
import {Annotation} from "../representation/scenario";

@Component({
  selector: 'app-annotations-token',
  templateUrl: './annotations-token.component.html',
  styleUrls: ['./annotations-token.component.css']
})
export class AnnotationsTokenComponent implements OnInit {
  @Input() data: Annotation<string>;

  constructor() { }

  ngOnInit(): void {
  }

}
