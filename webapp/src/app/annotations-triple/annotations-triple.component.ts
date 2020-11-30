import {Component, Input, OnInit} from '@angular/core';
import {Annotation} from "../representation/scenario";
import {EntityType, Triple} from "../representation/annotation";

@Component({
  selector: 'app-annotations-triple',
  templateUrl: './annotations-triple.component.html',
  styleUrls: ['./annotations-triple.component.css']
})
export class AnnotationsTripleComponent implements OnInit {
  @Input() data: Annotation<Triple>;

  entityTypes: string[];

  constructor() {
    this.entityTypes = Object.keys(EntityType).filter(k => !isNaN(EntityType[k]));
  }

  ngOnInit(): void {
  }

}
