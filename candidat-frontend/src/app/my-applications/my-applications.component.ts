import { Component, OnInit } from '@angular/core';
import { ApplicationService } from '../application.service';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-my-applications',
  templateUrl: './my-applications.component.html',
  styleUrls: ['./my-applications.component.css']
})
export class MyApplicationsComponent implements OnInit {
  candidatures: any[] = [];
  applicationsByCV: Record<string, { title: string, company: string, location: string }[]> = {};
  constructor(private http: HttpClient,private appService: ApplicationService) {}

  ngOnInit(): void {
    this.http.get<Record<string, { title: string, company: string, location: string }[]>>(
    'http://localhost:8000/applications_by_cv'
  ).subscribe({
    next: data => this.applicationsByCV = data,
    error: err => console.error("Erreur récupération des candidatures", err)
  });

  this.candidatures = this.appService.getApplications();
  }


}
