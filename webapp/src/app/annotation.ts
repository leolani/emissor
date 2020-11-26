import {AtomicContainer, Sequence} from "./container";

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

