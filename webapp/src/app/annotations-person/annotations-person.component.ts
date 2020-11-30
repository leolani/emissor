import {Component, Input, OnInit} from '@angular/core';
import {Annotation} from "../representation/scenario";
import {Person} from "../representation/entity";

@Component({
  selector: 'app-annotations-person',
  templateUrl: './annotations-person.component.html',
  styleUrls: ['./annotations-person.component.css']
})
export class AnnotationsPersonComponent implements OnInit {
  @Input() data: Annotation<Person>;

  constructor() { }

  ngOnInit(): void {
  }

}
