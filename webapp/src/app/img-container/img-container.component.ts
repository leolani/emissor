import {Component, ElementRef, HostListener, Input, OnInit, ViewChild} from '@angular/core';
import {BoundingBox} from "../container";

const enum Status {
  OFF = 0,
  RESIZE = 1,
  MOVE = 2
}

@Component({
  selector: 'app-img-container',
  templateUrl: './img-container.component.html',
  styleUrls: ['./img-container.component.css']
})
export class ImgContainerComponent implements OnInit {
  @Input() containerId: string;
  @Input() image: string;
  @Input() segments: BoundingBox[] = [new BoundingBox("test", 5,5,50,50)];

  selected: BoundingBox;
  status: number = 0;

  @ViewChild("container") public container: ElementRef;

  private containerPos: { left: number, top: number, right: number, bottom: number, width: number, height: number };
  private startPosition: number[];
  private mouseStart: {x: number, y: number};

  constructor() { }

  ngOnInit() {}

  private loadContainer() {
    const {left, top} = this.container.nativeElement.getBoundingClientRect();
    const width = this.container.nativeElement.clientWidth;
    const height = this.container.nativeElement.clientHeight;
    const right = left + width;
    const bottom = top + height;
    this.containerPos = { left, top, right, bottom, width, height };
  }

  select(segment: BoundingBox) {
    this.selected = this.selected ? null : segment;
    this.status = Status.OFF;
  }

  setStatus(event: MouseEvent, status: number) {
    if (!this.selected) {
      return;
    }

    event.stopPropagation();
    this.status = status;

    if (status !== Status.OFF) {
      this.loadContainer();
      this.startPosition = this.selected.bounds;
      this.mouseStart = { x: event.x, y: event.y };
    }
  }

  @HostListener('window:mousemove', ['$event'])
  onMouseMove(event: MouseEvent) {
    if (this.status === Status.RESIZE) {
      this.resize(event);
    } else if (this.status === Status.MOVE) {
      this.move(event);
    }
  }

  private resize(event: MouseEvent){
    let bounds = this.selected.bounds.slice();
    bounds[2] = Math.min(this.containerPos.width, Math.max(bounds[0], event.x - this.containerPos.left));
    bounds[3] = Math.min(this.containerPos.height, Math.max(bounds[1], event.y - this.containerPos.top));
    this.selected.bounds = bounds;
  }

  private move(event: MouseEvent){
    let dx = event.x - this.mouseStart.x;
    let dy = event.y - this.mouseStart.y;

    let bounds = this.startPosition.slice();
    bounds[0] += dx;
    bounds[1] += dy;
    bounds[2] += dx;
    bounds[3] += dy;

    if (this.insideContainer(bounds)) {
      this.selected.bounds = bounds;
    }
  }

  private insideContainer(bounds: number[]) {
    return bounds[0] >= 0 &&
      bounds[2] <= this.containerPos.width &&
      bounds[1] >= 0 &&
      bounds[3] <= this.containerPos.height;
  }
}



