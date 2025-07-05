import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Job {
  id?: number;
  description: string;
}

export interface CVInput {
  name: string;
  text: string;
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {

  private apiUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) { }

  getJobs(): Observable<Job[]> {
    return this.http.get<Job[]>(`${this.apiUrl}/jobs`);  // on ajoutera endpoint GET /jobs si besoin
  }

  saveJob(job: Job): Observable<any> {
    return this.http.post(`${this.apiUrl}/save_job`, job);
  }

  saveCV(cv: CVInput): Observable<any> {
    return this.http.post(`${this.apiUrl}/save_cv`, cv);
  }
}
