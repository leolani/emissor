import {AtomicContainer, Sequence} from "./container";
import {Annotation} from "./scenario";

enum ImageLabel {
  FACE
}

enum EntityType {
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
    case "token":
    case "diaplay":
    case "label":
      return annotation.value.value;
    case "Utterance":
      return annotation.value.utterance;
    case "Entity":
      return annotation.value.id + " - "+ annotation.value.type;
    case "token":
      return annotation.value;
  }
}