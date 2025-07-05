import { ComponentFixture, TestBed } from '@angular/core/testing';

import { JobOfferListComponent } from './job-offer-list.component';

describe('JobOfferListComponent', () => {
  let component: JobOfferListComponent;
  let fixture: ComponentFixture<JobOfferListComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [JobOfferListComponent]
    });
    fixture = TestBed.createComponent(JobOfferListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
