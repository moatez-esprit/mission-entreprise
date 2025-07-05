import { Component, OnInit } from '@angular/core';
import { ApiService, Job, CVInput } from '../api.service';

@Component({
  selector: 'app-upload-cv',
  templateUrl: './upload-cv.component.html',
  styleUrls: ['./upload-cv.component.css']
})
export class UploadCvComponent implements OnInit {

  jobs: Job[] = [];
  selectedJobId: number | null = null;

  cvFile: File | null = null;
  cvName: string = '';
  cvText: string = '';

  message: string = '';

  constructor(private apiService: ApiService) { }

  ngOnInit(): void {
    this.loadJobs();
  }

  loadJobs() {
    this.apiService.getJobs().subscribe(
      jobs => this.jobs = jobs,
      err => console.error(err)
    );
  }

  onFileChange(event: any) {
    if (event.target.files.length > 0) {
      this.cvFile = event.target.files[0];
      this.cvName = this.cvFile!.name;  // Ajout du ! pour dire à TypeScript que ce n’est pas null

      const reader = new FileReader();
      reader.onload = (e: any) => {
        this.cvText = e.target.result;
      };
      reader.readAsText(this.cvFile!); // même chose ici
    }
  }


  onSubmit() {
    if (!this.cvFile || !this.selectedJobId) {
      this.message = 'Veuillez sélectionner une offre et un fichier CV.';
      return;
    }

    // On récupère l'offre sélectionnée
    const selectedJob = this.jobs.find(j => j.id === this.selectedJobId);
    if (!selectedJob) {
      this.message = 'Offre invalide.';
      return;
    }

    // Sauvegarde du job (si pas déjà fait)
    this.apiService.saveJob(selectedJob).subscribe(() => {
      // Puis sauvegarde du CV
      const cvInput: CVInput = {
        name: this.cvName,
        text: this.cvText
      };
      this.apiService.saveCV(cvInput).subscribe(() => {
        this.message = 'CV et offre sauvegardés avec succès !';
        // reset form
        this.cvFile = null;
        this.cvName = '';
        this.cvText = '';
        this.selectedJobId = null;
      }, err => {
        this.message = 'Erreur lors de la sauvegarde du CV.';
      });
    }, err => {
      this.message = 'Erreur lors de la sauvegarde de l\'offre.';
    });
  }
}
