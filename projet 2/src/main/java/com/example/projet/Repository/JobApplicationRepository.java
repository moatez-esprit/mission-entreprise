package com.example.projet.Repository;

import com.example.projet.Entities.JobApplication;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface JobApplicationRepository extends JpaRepository<JobApplication, Long> {
    boolean existsByApplicantEmailAndJobOfferId(String applicantEmail, Long jobOfferId);
    JobApplication findByApplicantEmailAndJobOfferId(String applicantEmail, Long jobOfferId);

    // New method to find all applications by job offer ID
    java.util.List<JobApplication> findByJobOfferId(Long jobOfferId);
}
