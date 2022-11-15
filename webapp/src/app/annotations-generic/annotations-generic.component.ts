import {Component, Input, OnInit} from '@angular/core';
import {Annotation} from "../representation/scenario";

@Component({
  selector: 'app-annotations-generic',
  templateUrl: './annotations-generic.component.html',
  styleUrls: ['./annotations-generic.component.css']
})
export class AnnotationsGenericComponent implements OnInit {
  @Input() data: Annotation<any>;

  display: string

  constructor() { }

  ngOnInit(): void {
    if (this.data.value !== Object(this.data.value)) {
      this.display = this.data.value;
    } else if ("display" in this.data.value && this.data.value.display) {
      this.display = this.data.value.display;
    } else if ("name" in this.data.value && this.data.value.name) {
      this.display = this.data.value.name;
    } else if ("label" in this.data.value && this.data.value.label) {
      this.display = this.data.value.label;
    } else if ("value" in this.data.value && this.data.value.value) {
      this.display = this.data.value.value;
    } else {
      this.display = this.data.toString();
    }
  }

}
