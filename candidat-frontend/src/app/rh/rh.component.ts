import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-rh',
  templateUrl: './rh.component.html'
})
export class RhComponent implements OnInit {
  jobs: any[] = [];
  selectedCvs: any[] = [];
  selectedJobId: number | null = null;
  testDates: { [jobId: number]: string } = {};



  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.http.get<any[]>('http://localhost:8000/jobs').subscribe(data => {
      this.jobs = data;
    });
    this.http.get<any[]>('http://localhost:8000/jobs').subscribe(jobs => {
  this.jobs = jobs;
  this.testDates = {}; // reset

  this.jobs.forEach(job => {
    this.http.get<{ test_date: string }>(`http://localhost:8000/get_test_date/${job.id}`)
      .subscribe(result => {
        if (result && result.test_date) {
          console.log(`Job ${job.id} - Date trouvée :`, result.test_date);
          this.testDates[job.id] = result.test_date;
        } else {
          console.log(`Job ${job.id} - Aucune date trouvée`);
        }
      }, error => {
        console.error(`Erreur lors de la récupération de la date pour le job ${job.id}`, error);
      });
  });
  });

  }

  viewApplications(job: any) {
  this.selectedJobId = job.id;
  this.http.get<any[]>(`http://localhost:8000/applications/${job.id}`).subscribe(cvs => {
    this.selectedCvs = cvs;
  });
  this.jobs.forEach(job => {
  this.http.get<{ test_date: string }>(`http://localhost:8000/get_test_date/${job.id}`)
    .subscribe(result => {
      if (result.test_date) {
        this.testDates[job.id] = result.test_date;
      }
    });
  });
}

  onMatch(job: any) {
  this.http.get<any[]>('http://localhost:8000/cvs').subscribe(cvs => {
    const payload = { job_description: job.description, cvs: cvs };
    
    this.http.post('http://localhost:8000/match', payload).subscribe((result: any) => {
      // ✅ Affiche le score
      alert(`Meilleur CV: ${result.best_cv_name} avec score: ${result.best_similarity_score}`);

      // ✅ Enregistre côté backend
      this.http.post('http://localhost:8000/send_match_result', null, {
        params: {
          job_id: job.id,
          cv_name: result.best_cv_name,
          score: result.best_similarity_score
        }
      }).subscribe(() => {
        console.log("✅ Résultat enregistré côté serveur");
      });
    });
  });
  }

}
