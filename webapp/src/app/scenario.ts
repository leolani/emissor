import {Ruler, TimeRuler} from "./container";
import {Annotation, Mention} from "./annotation";
import {ScenarioService} from "./scenario.service";
import {ContainerComponent} from "./container/container.component";
import {Type} from "@angular/core";
import {SegmentComponent} from "./segment/segment.component";
import {ContainerItem} from "./container/container-item";

export interface Scenario {
  id: string;
  name: string;
  start: number;
  end: number;
  signals: Map<string, string>;
}

export class Signal {
  id: number;
  name: string;
  time: TimeRuler;
  mentions: Mention<any>[];

  constructor(id: number, name: string, time: TimeRuler, mentions: Mention<any>[]) {
    this.id = id;
    this.name = name;
    this.time = time;
    this.mentions = mentions;
  }
}

export class ImageSignal extends Signal {
  image: string;

  constructor(id: number, name: string, time: TimeRuler, mentions: Mention<any>[], image: string) {
    super(id, name, time, mentions);
    this.image = image;
  }
}

export class TextSignal extends Signal {
  text: string;

  constructor(id: number, name: string, time: TimeRuler, mentions: Mention<any>[], text: string) {
    super(id, name, time, mentions);
    this.text = text;
  }
}

