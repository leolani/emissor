import {Annotation} from "../representation/scenario";

export interface AnnotationComponent<T> {
  data: Annotation<T>;
}
