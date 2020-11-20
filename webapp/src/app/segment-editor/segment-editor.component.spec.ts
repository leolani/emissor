import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SegmentEditorComponent } from './segment-editor.component';

describe('SegmentEditorComponent', () => {
  let component: SegmentEditorComponent;
  let fixture: ComponentFixture<SegmentEditorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SegmentEditorComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(SegmentEditorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
