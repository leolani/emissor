import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AnnotationEditorComponent } from './annotation-editor.component';

describe('SegmentEditorComponent', () => {
  let component: AnnotationEditorComponent;
  let fixture: ComponentFixture<AnnotationEditorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AnnotationEditorComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(AnnotationEditorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
