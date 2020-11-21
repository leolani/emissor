import {AfterViewInit, Component, ElementRef, Input, OnChanges, OnInit, ViewChild} from '@angular/core';
import {ImageSignal} from "../scenario";
import {ContainerItem} from "../container/container-item";
import {ScenarioService} from "../scenario.service";

@Component({
  selector: 'app-carousel',
  templateUrl: './carousel.component.html',
  styleUrls: ['./carousel.component.css']
})
export class CarouselComponent implements OnInit, OnChanges {
  @Input() signals: ImageSignal[];
  @Input() selected: number;

  containerItem: ContainerItem<any, any>;

  constructor(private scenarioService: ScenarioService) { }

  ngOnInit(): void {
  }

  ngOnChanges(changes) {
    let selected = (changes.selected && changes.selected.currentValue) || this.selected || 0;
    let container = this.scenarioService.getContainerComponent(this.signals[selected]);
    this.containerItem = new ContainerItem(container, this.signals[selected], null);
  }

  // drawImageOnCanvas(context: CanvasRenderingContext2D, image: HTMLImageElement): void {
  //   this.context.clearRect(0,0, this.context.canvas.width, this.context.canvas.height);
  //
  //   let imgWidth = image.width;
  //   let imgHeight = image.height;
  //   let canvasWidth = this.context.canvas.width;
  //   let canvasHeight = this.context.canvas.height;
  //
  //   let hScale = canvasWidth/imgWidth;
  //   let vScale = canvasHeight/imgHeight;
  //   let scale = Math.min(hScale, vScale);
  //
  //   let scaledWidth = Math.floor(scale * imgWidth);
  //   let scaledHeight = Math.floor(scale * imgHeight);
  //   let dx = Math.floor((canvasWidth - scaledWidth) / 2);
  //   let dy= Math.floor((canvasHeight - scaledHeight) / 2);
  //
  //   this.context.drawImage(image, dx, dy, scaledWidth, scaledHeight);
  // }
}
