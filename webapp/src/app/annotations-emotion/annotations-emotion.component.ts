import {Component, Input, OnInit} from '@angular/core';
import {Annotation} from "../representation/scenario";
import {Emotion} from "../representation/entity";

@Component({
  selector: 'app-annotations-emotion',
  templateUrl: './annotations-emotion.component.html',
  styleUrls: ['./annotations-emotion.component.css']
})
export class AnnotationsEmotionComponent implements OnInit {
  @Input() data: Annotation<Emotion>;
  constructor() { }

  ngOnInit(): void {
  }

}
