import {AtomicContainer, Sequence} from "./container";
import {Annotation} from "./scenario";

enum ImageLabel {
  FACE
}

export enum EntityType {
  PERSON, FRIEND, OBJECT = 2
}

export interface Entity {
  id: string;
  type: EntityType;
}

export interface Triple {
  subject: Entity
  predicate: string;
  object: Entity
}

export interface Token extends AtomicContainer<string> {
  // no additional fields
}

export interface Utterance extends Sequence<Token> {
  chat_id: string;
  utterance: string;
  tokens: Token[]
}

export interface Display {
  display: string;
}

export function annotationDisplayValue(annotation: Annotation<any>): string {
  switch (annotation.type.toLowerCase()) {
    case "display":
    case "conversationalagent":
    case "label":
    case "pos":
    case "emotion":
      return annotation.value;
    case "triple":
      return annotation.value.subject.id + annotation.value.predicate + annotation.value.object.id;
    case "utterance":
      return annotation.value.utterance;
    case "entity":
      return annotation.value.id + " - " + annotation.value.type;
    case "person":
      return annotation.value.name;
    case "object":
      return annotation.value.label;
    case "token":
      return annotation.value.value || annotation.value;
    default:
      if (annotation.value !== Object(annotation.value)) {
        // pass
      } else if("display" in annotation.value && annotation.value.display) {
        return annotation.value.display;
      } else if ("name" in annotation.value && annotation.value.name) {
        return annotation.value.name;
      } else if ("label" in annotation.value && annotation.value.label) {
        return annotation.value.label;
      }

      return annotation.type.startsWith("python-type:") ?
          annotation.type.split('.').slice(-1)[0] :
          annotation.type;
  }
}
