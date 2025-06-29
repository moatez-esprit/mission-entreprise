package com.example.projet.contoller;

import com.example.projet.Entities.JobApplication;
import com.example.projet.services.JobApplicationService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/applications")
@CrossOrigin(origins = "*")
public class JobApplicationController {

    @Autowired
    private JobApplicationService jobApplicationService;

    @PostMapping
    public ResponseEntity<?> submitApplication(
            @RequestPart("application") JobApplication application,
            @RequestPart("cvFile") MultipartFile cvFile) {
        try {
            JobApplication savedApplication = jobApplicationService.submitApplication(application, cvFile);
            return ResponseEntity.ok(savedApplication);
        } catch (IOException e) {
            if (e.getMessage().contains("already applied")) {
                Map<String, String> errorResponse = new HashMap<>();
                errorResponse.put("message", "User has already applied to this job");
                return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(errorResponse);
            }
            Map<String, String> errorResponse = new HashMap<>();
            errorResponse.put("message", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }

    // New endpoint to get all applications for a job
    @GetMapping("/job/{jobId}")
    public ResponseEntity<?> getApplicationsByJobId(@PathVariable Long jobId) {
        try {
            return ResponseEntity.ok(jobApplicationService.getApplicationsByJobId(jobId));
        } catch (Exception e) {
            Map<String, String> errorResponse = new HashMap<>();
            errorResponse.put("message", "Error retrieving applications");
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }
}
