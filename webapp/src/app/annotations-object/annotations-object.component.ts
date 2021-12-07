import {Component, Input, OnInit} from '@angular/core';
import {Annotation} from "../representation/scenario";
import {Obj} from "../representation/entity";

@Component({
  selector: 'app-annotations-object',
  templateUrl: './annotations-object.component.html',
  styleUrls: ['./annotations-object.component.css']
})
export class AnnotationsObjectComponent implements OnInit {
  @Input() data: Annotation<Obj>;

  constructor() { }

  ngOnInit(): void {
  }

}
