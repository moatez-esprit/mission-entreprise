import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
})
export class AppComponent {
  isCandidate = false;

  constructor(private router: Router) {
    this.isCandidate = localStorage.getItem('role') === 'candidat';
  }

  logout() {
    localStorage.removeItem('role');
    this.router.navigate(['/']);
  }
}
