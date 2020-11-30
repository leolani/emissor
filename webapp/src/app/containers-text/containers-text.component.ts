import {Component, EventEmitter, Input, OnChanges, OnInit, Output, SimpleChanges} from '@angular/core';
import {Index} from "../representation/container";
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
  private selectedContainerIds: Set<any>;

  constructor(private scenarioService: ScenarioService, private componentService: ComponentService) {}

  ngOnInit(): void {
    this.tokens = this.selection.signal.mentions.filter(mention =>
        mention.segment.length === 1
        && mention.segment[0].container_id === this.selection.signal.id
        && mention.annotations.length
        && mention.annotations[0].type.toLowerCase() === "token");
    this.setContainerIds(this.selection);
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

  tokenClass(idx: number) {
    if (this.selectedContainerIds.has(this.tokens[idx].annotations[0].value.id)) {
      return "selected";
    }
  }

  select(idx: number, token: Mention, $event: MouseEvent) {
    if (this.tokenClass(idx) === "selected") {
      this.selectedContainerIds.delete(token.annotations[0].value.id);
      this.selection.mention.segment = this.selection.mention.segment
          .filter(seg => seg.container_id !== token.annotations[0].value.id)
    } else {
      this.selectedContainerIds.add(token.annotations[0].value.id);
      this.selection.addSegment("atomic", token.annotations[0].value.id).then(selection => {
        this.selection = selection;
        this.selectionChange.emit(this.selection);
      });
    }
    this.selection = this.selection.withMention(this.selection.mention);
    this.selectionChange.emit(this.selection);
  }

  addMention() {
    this.selection.addMention().then(selection => {
      this.selection = selection;
      this.selectionChange.emit(this.selection);
    });
  }

  addAnnotation() {
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
  }
}
