import {Component, Input, OnInit} from '@angular/core';
import {Annotation} from "../representation/scenario";

@Component({
  selector: 'app-annotations-generic',
  templateUrl: './annotations-generic.component.html',
  styleUrls: ['./annotations-generic.component.css']
})
export class AnnotationsGenericComponent implements OnInit {
  @Input() data: Annotation<any>;

  constructor() { }

  ngOnInit(): void {
  }

}
