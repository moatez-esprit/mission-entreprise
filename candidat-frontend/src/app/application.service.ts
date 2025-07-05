import { Injectable } from '@angular/core';
import { JobOffer } from './job-offer-list/job-offer-list.component';

@Injectable({
  providedIn: 'root'
})
export class ApplicationService {
  candidatures: { offer: JobOffer, cvName: string }[] = [];

  addApplication(offer: JobOffer, cvName: string) {
    // Vérifie si déjà postulé
    const exists = this.candidatures.some(c => c.offer.id === offer.id && c.cvName === cvName);
    if (!exists) {
      this.candidatures.push({ offer, cvName });
    }
  }

  getApplications() {
    return this.candidatures;
  }
}
