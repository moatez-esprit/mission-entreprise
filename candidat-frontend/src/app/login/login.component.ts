import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html'
})
export class LoginComponent {
  username = '';
  password = '';
  errorMessage = '';
  constructor(private http: HttpClient,private router: Router) {}

  loginAs(role: string) {
    if (role === 'rh') {
      this.router.navigate(['/rh']);
    } else if (role === 'candidat') {
      this.router.navigate(['/candidat']);
    }
  }

  role = 'candidat';  // valeur par défaut

login() {
  const payload = {
    username: this.username,
    role: this.role
  };

  this.http.post<any>('http://localhost:8000/login', payload).subscribe({
    next: (response) => {
      if (response.role === 'rh') {
        this.router.navigate(['/rh']);
      } else if (response.role === 'candidat') {
        this.router.navigate(['/candidat']);
      } else {
        this.errorMessage = 'Rôle non reconnu';
      }
    },
    error: (err) => {
      this.errorMessage = err.error?.detail || "Erreur de connexion";
    }
  });
}
}
