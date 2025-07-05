import { Component, ViewChild, ElementRef, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Location } from '@angular/common';
import { ApplicationService } from '../application.service';
import { Router } from '@angular/router';

export interface JobOffer {
  id: number;
  title: string;
  company: string;
  location: string;
  description: string;
  matchResult?: {
    best_cv_name: string;
    score: number;
  };
}

@Component({
  selector: 'app-job-offer-list',
  templateUrl: './job-offer-list.component.html',
  styleUrls: ['./job-offer-list.component.css']
})
export class JobOfferListComponent implements OnInit {
  offers: JobOffer[] = [];
  selectedId: number | null = null;
  selectedOfferForCV: JobOffer | null = null;
  selectedOfferDetails: JobOffer | null = null;
  candidatures: { offer: JobOffer, cvName: string }[] = [];
  bestResultMessage: string = '';
  cvName: string = '';
  showScores: boolean = false;
  selectedTestDates: { [jobId: number]: string } = {};




  @ViewChild('fileInput') fileInputRef!: ElementRef;

  constructor(
  private http: HttpClient,
  private location: Location,
  private appService: ApplicationService,
  private router: Router  // ✅
) {}

  ngOnInit(): void {
  this.http.get<JobOffer[]>('http://localhost:8000/jobs').subscribe({
    next: (jobs) => {
      this.offers = jobs;

      // charger les notifications pour chaque job
      this.offers.forEach(job => {
        this.http.get<{ best_cv_name: string; score: number }>(
          `http://localhost:8000/get_match_result/${job.id}`
        ).subscribe(result => {
          job.matchResult = result;
        });
      });
    },
    error: (err) => {
      console.error('Erreur de récupération des offres :', err);
    }
  });

  this.cvName = localStorage.getItem('cvName') || '';
  
}


  onSelect(offer: JobOffer) {
  this.selectedOfferDetails = offer;
}

  goBack() {
  this.router.navigate(['/']); // ou router.navigate(['/'])
  }

  triggerFileUpload(offer: JobOffer) {
    this.selectedOfferForCV = offer;
    this.fileInputRef.nativeElement.click();
  }

  onFileSelected(event: any) {
  const file: File = event.target.files[0];
  if (file && this.selectedOfferForCV) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('job_id', this.selectedOfferForCV.id.toString());

    this.http.post('http://localhost:8000/api/upload-cv', formData).subscribe({
      next: () => {
        alert(`CV '${file.name}' postulé avec succès à l'offre '${this.selectedOfferForCV?.title}'`);
        this.appService.addApplication(this.selectedOfferForCV!, file.name); // ✅
        // Optionnel : ajouter cette postulation localement pour l’afficher sans recharger
        this.candidatures.push({
          offer: this.selectedOfferForCV!,  // 👈 le point d’exclamation dit à TypeScript "c'est pas null"
          cvName: file.name
        });
      },
      error: () => alert('Erreur CV existe')
    });
  }
  }

  onDateSelected(event: any, jobId: number) {
  const selectedDate = event.target.value;
  this.selectedTestDates[jobId] = selectedDate;

  // Optionnel : Tu peux envoyer cette date vers le backend
  this.http.post('http://localhost:8000/save_test_date', {
    job_id: jobId,
    date: selectedDate
  }).subscribe({
    next: () => {
      console.log("Date enregistrée");
    },
    error: (err) => {
      console.error("Erreur enregistrement date", err);
    }
  });
}

}
