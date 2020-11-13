import {Component, Input, OnInit} from '@angular/core';
import {Scenario, Signal} from "../scenario";
import {Annotation, Mention} from "../annotation";

@Component({
  selector: 'app-annotation',
  templateUrl: './annotation.component.html',
  styleUrls: ['./annotation.component.css']
})
export class AnnotationComponent implements OnInit {
  @Input() signal: Signal;

  selectedMention: Mention;
  selectedAnnotation: Annotation;

  constructor() { }

  ngOnInit(): void {
    console.log(this.signal);
    this.selectedMention = this.signal.mentions.length && this.signal.mentions[0]
    this.selectedAnnotation = this.selectedMention && this.selectedMention.annotations.length
                              && this.selectedMention.annotations[0]
  }

  addAnnotation() {
    let len = this.selectedMention.annotations.length;
    let previous = len && this.selectedMention.annotations[len - 1];
    this.selectedMention.annotations.push({
      name: "" + len,
      src: (previous && previous.src) || "",
      timestamp: new Date().getTime(),
      value: "",
      type: (previous && previous.type) || ""
    })
  }
}
