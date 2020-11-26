import {Component, ElementRef, HostListener, Input, OnChanges, OnInit, SimpleChanges, ViewChild} from '@angular/core';
import {MultiIndex} from "../representation/container";
import {ImageSignal} from "../representation/scenario";
import {ContainerComponent} from "../container/container.component";
import {SignalSelection} from "../signal-selection";

const enum Status {
  OFF = 0,
  RESIZE = 1,
  MOVE = 2
}

@Component({
  templateUrl: './containers-img.component.html',
  styleUrls: ['./containers-img.component.css']
})
export class ContainersImgComponent implements OnInit, OnChanges, ContainerComponent<ImageSignal, MultiIndex> {
  @Input() data: ImageSignal;
  @Input() selection: SignalSelection;

  segments: MultiIndex[];
  selected: MultiIndex;

  status: number = 0;

  @ViewChild("container") public rootContainer: ElementRef;
  @ViewChild("img_container") public container: ElementRef;
  @ViewChild("image") public image: ElementRef;

  scale: number = 1;
  leftOffset: number = 0;
  topOffset: number = 0;
  scaledWidth: number;
  scaledHeight: number;
  imageWidth: number;

  private containerPos: { left: number, top: number, right: number, bottom: number, width: number, height: number };
  private startPosition: number[];
  private mouseStart: {x: number, y: number};

  constructor() { }

  ngOnInit() {
    this.segments = <MultiIndex[]> this.data.mentions.flatMap(mention => mention.segment)
      .filter(seg => seg.type.toLowerCase() === "multiindex");
  }

  ngOnChanges(changes: SimpleChanges) {
    console.log(changes);
    if (changes.selection) {
      this.selected = changes.selection.currentValue.segment;
    }
  }

  positionImage(): void {
    let image = this.image.nativeElement
    let imgWidth = image.width;
    let imgHeight = image.height;
    let canvasWidth = this.rootContainer.nativeElement.clientWidth;
    let canvasHeight = this.rootContainer.nativeElement.clientHeight;

    let hScale = canvasWidth/imgWidth;
    let vScale = canvasHeight/imgHeight;
    this.scale = Math.min(hScale, vScale);

    this.scaledWidth = Math.floor(this.scale * imgWidth);
    this.scaledHeight = Math.floor(this.scale * imgHeight);
    this.leftOffset = Math.floor((canvasWidth - this.scaledWidth) / 2);
    this.topOffset = Math.floor((canvasHeight - this.scaledHeight) / 2);
    this.imageWidth = 100;
  }

  private loadContainer() {
    const {left, top} = this.container.nativeElement.getBoundingClientRect();
    const width = this.container.nativeElement.clientWidth;
    const height = this.container.nativeElement.clientHeight;
    const right = left + width;
    const bottom = top + height;
    this.containerPos = { left, top, right, bottom, width, height };
  }

  select(segment: MultiIndex) {
    if (segment === this.selection.segment) {
      this.selected = this.selected ? null : segment;
      this.status = Status.OFF;
    } else {
      this.selected = null;
    }
  }

  private setSelection() {
    this.selection = this.selection.withSegment(this.selected);
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
    let bounds = this.scaleArray(this.selected.bounds);
    bounds[2] = Math.min(this.containerPos.width, Math.max(bounds[0], event.x - this.containerPos.left));
    bounds[3] = Math.min(this.containerPos.height, Math.max(bounds[1], event.y - this.containerPos.top));
    this.selected.bounds = this.unscaleArray(bounds);
    this.setSelection();
  }

  private move(event: MouseEvent){
    let dx = event.x - this.mouseStart.x;
    let dy = event.y - this.mouseStart.y;

    let bounds = this.scaleArray(this.startPosition);
    bounds[0] += dx;
    bounds[1] += dy;
    bounds[2] += dx;
    bounds[3] += dy;

    if (this.insideContainer(bounds)) {
      this.selected.bounds = this.unscaleArray(bounds);
      this.setSelection();
    }
  }

  private insideContainer(bounds: number[]) {
    return bounds[0] >= 0 &&
      bounds[2] <= this.containerPos.width &&
      bounds[1] >= 0 &&
      bounds[3] <= this.containerPos.height;
  }

  private scaleArray(arr) {
    return arr.map(x => x * this.scale);
  }

  private unscaleArray(arr) {
    return arr.map(x => Math.max(3, Math.round(x / this.scale)));
  }
}



