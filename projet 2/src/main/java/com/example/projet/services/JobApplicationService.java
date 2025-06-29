package com.example.projet.services;

import com.example.projet.Entities.JobApplication;
import com.example.projet.Repository.JobApplicationRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.*;
import java.time.LocalDate;

@Service
public class JobApplicationService {

    private final String UPLOAD_DIR = "uploads/applications/";

    @Autowired
    private JobApplicationRepository jobApplicationRepository;

    public JobApplication submitApplication(JobApplication application, MultipartFile cvFile) throws IOException {
        System.out.println("submitApplication called for email: " + application.getApplicantEmail() + ", jobOfferId: " + application.getJobOfferId());
        // Normalize email to lowercase for consistent checking
        String normalizedEmail = application.getApplicantEmail().toLowerCase();

        // Check if user has already applied to this job
        JobApplication existingApplication = jobApplicationRepository.findByApplicantEmailAndJobOfferId(normalizedEmail, application.getJobOfferId());
        if (existingApplication != null) {
            System.out.println("Duplicate application detected for email: " + normalizedEmail + ", jobOfferId: " + application.getJobOfferId());
            // User already applied, throw exception to indicate duplicate application
            throw new IOException("User has already applied to this job");
        }

        // Create upload directory if not exists
        Files.createDirectories(Paths.get(UPLOAD_DIR));

        String filename = System.currentTimeMillis() + "_" + cvFile.getOriginalFilename();
        Path filePath = Paths.get(UPLOAD_DIR + filename);

        // Save the CV file
        Files.copy(cvFile.getInputStream(), filePath, StandardCopyOption.REPLACE_EXISTING);

        // Set CV file path and application date
        application.setCvFilePath(filePath.toString());
        application.setApplicationDate(LocalDate.now());

        // Save application
        return jobApplicationRepository.save(application);
    }

    // New method to get applications by job ID
    public java.util.List<JobApplication> getApplicationsByJobId(Long jobId) {
        return jobApplicationRepository.findByJobOfferId(jobId);
    }
}
