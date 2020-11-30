import {Component, EventEmitter, Input, OnChanges, OnInit, Output, SimpleChanges, AfterViewInit} from '@angular/core';
import {ContainerComponent} from "../container/container.component";
import {Mention, TextSignal} from "../representation/scenario";
import {SignalSelection} from "../signal-selection";
import {ScenarioService} from "../scenario.service";
import {ComponentService} from "../component.service";

@Component({
  templateUrl: './containers-text.component.html',
  styleUrls: ['./containers-text.component.css']
})
export class ContainersTextComponent implements OnInit, OnChanges, ContainerComponent<TextSignal> {
  @Input() selection: SignalSelection<TextSignal>;
  @Output() selectionChange = new EventEmitter<SignalSelection<any>>();

  tokens: Mention[];
  annotationType: string;
  selectedContainerIds: Set<any>;

  constructor(private scenarioService: ScenarioService, private componentService: ComponentService) {}

  ngOnInit(): void {
    this.setContainerIds(this.selection);

    this.tokens = this.selection.signal.mentions.filter(mention =>
        mention.segment.length === 1
        && mention.segment[0].container_id === this.selection.signal.id
        && mention.annotations.length
        && mention.annotations[0].type.toLowerCase() === "token");
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes.selection
      && changes.selection.currentValue.mention !== changes.selection.previousValue.mention) {
      this.setContainerIds(changes.selection.currentValue);
    }
  }

  private setContainerIds(selection: SignalSelection<any>) {
    this.selectedContainerIds = selection.mention ?
        new Set(selection.mention.segment.map(seg => seg.container_id)) :
        new Set();
  }

  counter(range: number) {
    return Array.from(Array(range).keys());
  }

  select(idx: number, token: Mention, $event: MouseEvent) {
    if (!this.selection.mention) {
      return;
    }

    let token_container = token.annotations[0].value.id;
    if (this.selectedContainerIds.has(token_container)) {
      this.selectedContainerIds.delete(token_container);
      this.selection = this.selection.removeSegment(token_container);
    } else {
      this.selectedContainerIds.add(token_container);
      this.selection.addSegment("atomic", token_container).then(selection => {
        this.selection = selection;
      });
    }
  }

  addMention() {
    this.save();
    this.selection.addMention().then(selection => {
      this.selection = selection;
      this.selectionChange.emit(this.selection);
    });
  }

  addAnnotation() {
    this.save();
    this.selection.addAnnotation(this.annotationType).then(selection => {
      this.selection = selection;
      this.selectionChange.emit(this.selection);
    });
  }

  getAnnotationTypes(): string[] {
    return this.componentService.getAnnotationTypes();
  }

  save() {
    this.scenarioService.saveSignal(this.selection.scenarioId, this.selection.signal);
    this.selectionChange.emit(this.selection);
  }
}
