import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

import { AppComponent } from './app.component';
import { UploadCvComponent } from './upload-cv/upload-cv.component';
import { JobOfferListComponent } from './job-offer-list/job-offer-list.component';
import { CandidatComponent } from './candidat/candidat.component';
import { LoginComponent } from './login/login.component';
import { RhComponent } from './rh/rh.component';
import { MyApplicationsComponent } from './my-applications/my-applications.component';
import { AboutComponent } from './about/about.component';
import { ContactComponent } from './contact/contact.component';

@NgModule({
  declarations: [
    AppComponent,
    UploadCvComponent,
    JobOfferListComponent,
    CandidatComponent,
    LoginComponent,
    RhComponent,
    MyApplicationsComponent,
    AboutComponent,
    ContactComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    FormsModule,
    HttpClientModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
