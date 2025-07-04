package com.example.projet.services;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Service
public class LinkedInService {

    @Value("${linkedin.access.token}")
    private String accessToken;

    @Value("${linkedin.organization.id}")
    private String organizationId; // Your company page ID

    public void postJobToLinkedIn(String title, String description, String location, String salaryRange, String department) {
        String apiUrl = "https://api.linkedin.com/v2/ugcPosts";

        String postContent = String.format(
            "%s\n\nDépartement: %s\nLocalisation: %s\nSalaire: %s\n\n%s",
            title, department, location, salaryRange, description
        );

        String body = "{"
            + "\"author\": \"urn:li:organization:" + organizationId + "\","
            + "\"lifecycleState\": \"PUBLISHED\","
            + "\"specificContent\": {"
            + "  \"com.linkedin.ugc.ShareContent\": {"
            + "    \"shareCommentary\": {\"text\": \"" + postContent.replace("\"", "\\\"") + "\"},"
            + "    \"shareMediaCategory\": \"NONE\""
            + "  }"
            + "},"
            + "\"visibility\": {\"com.linkedin.ugc.MemberNetworkVisibility\": \"PUBLIC\"}"
            + "}";

        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth(accessToken);
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<String> request = new HttpEntity<>(body, headers);

        RestTemplate restTemplate = new RestTemplate();
        ResponseEntity<String> response = restTemplate.postForEntity(apiUrl, request, String.class);

        if (!response.getStatusCode().is2xxSuccessful()) {
            throw new RuntimeException("Failed to post to LinkedIn: " + response.getBody());
        }
    }
}