import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ImgContainerComponent } from './img-container.component';

describe('ImgContainerComponent', () => {
  let component: ImgContainerComponent;
  let fixture: ComponentFixture<ImgContainerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ImgContainerComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ImgContainerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
