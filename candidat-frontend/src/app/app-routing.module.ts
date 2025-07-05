import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoginComponent } from './login/login.component';
import { RhComponent } from './rh/rh.component';
import { CandidatComponent } from './candidat/candidat.component';
import { JobOfferListComponent } from './job-offer-list/job-offer-list.component';
import { UploadCvComponent } from './upload-cv/upload-cv.component';
import { MyApplicationsComponent } from './my-applications/my-applications.component';
import { AboutComponent } from './about/about.component';
import { ContactComponent } from './contact/contact.component';

const routes: Routes = [
  { path: '', component: LoginComponent },
  { path: 'rh', component: RhComponent },
  { path: 'candidat', component: JobOfferListComponent },
  { path: 'mes-postulations', component: MyApplicationsComponent }, // 🟢 accessible uniquement pour candidat
  { path: 'about', component: AboutComponent },
  { path: 'contact', component: ContactComponent },
  { path: '**', redirectTo: '' }
];
  

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}
