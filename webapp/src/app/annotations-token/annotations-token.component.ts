import {Component, Input, OnInit} from '@angular/core';
import {Annotation} from "../representation/scenario";
import {Token} from "../representation/annotation";

@Component({
  selector: 'app-annotations-token',
  templateUrl: './annotations-token.component.html',
  styleUrls: ['./annotations-token.component.css']
})
export class AnnotationsTokenComponent implements OnInit {
  @Input() data: Annotation<Token>;

  constructor() { }

  ngOnInit(): void {
  }

}
