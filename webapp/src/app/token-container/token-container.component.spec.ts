import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TokenContainerComponent } from './token-container.component';

describe('TokenContainerComponent', () => {
  let component: TokenContainerComponent;
  let fixture: ComponentFixture<TokenContainerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TokenContainerComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TokenContainerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
