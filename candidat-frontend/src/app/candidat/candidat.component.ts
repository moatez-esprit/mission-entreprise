import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-candidat',
  templateUrl: './candidat.component.html',
  styleUrls: ['./candidat.component.scss']
})
export class CandidatComponent implements OnInit {
  jobOffers: any[] = [];
  selectedOffer: any = null;
  cvFile: File | null = null;
  matchResult: any = null;
  applicationsByCV: any = {};


  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.loadJobOffers();
    this.http.get('http://localhost:8000/applications_by_cv').subscribe({
      next: data => this.applicationsByCV = data,
      error: err => console.error("Erreur récupération des candidatures", err)
    });
  }

  loadJobOffers(): void {
    this.http.get<any[]>('http://localhost:8000/api/offres').subscribe(data => {
      this.jobOffers = data;
    });
  }

  selectOffer(offer: any): void {
    this.selectedOffer = offer;
    this.matchResult = null;
  }

  onFileSelected(event: any): void {
    this.cvFile = event.target.files[0] || null;
  }

  onMatch(): void {
    if (!this.selectedOffer || !this.cvFile) return;

    const formData = new FormData();
    formData.append('cv', this.cvFile);
    formData.append('job_description', this.selectedOffer.description);

    this.http.post<any>('http://localhost:8000/api/match', formData).subscribe(
      res => this.matchResult = res,
      err => alert("Erreur lors de la comparaison du CV.")
    );
  }

}
