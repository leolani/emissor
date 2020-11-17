import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BoundingboxComponent } from './boundingbox.component';

describe('BoundingboxComponent', () => {
  let component: BoundingboxComponent;
  let fixture: ComponentFixture<BoundingboxComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ BoundingboxComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(BoundingboxComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
