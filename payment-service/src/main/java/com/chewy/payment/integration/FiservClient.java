package com.chewy.payment.integration;

import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.http.*;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

import java.time.Duration;
import java.util.Map;

@Component
public class FiservClient implements FiservService {

    private final RestTemplate restTemplate;
    private final String baseUrl;
    private final String apiKey;

    public FiservClient(RestTemplateBuilder builder, @org.springframework.beans.factory.annotation.Value("${fiserv.url:}") String baseUrl,
                        @org.springframework.beans.factory.annotation.Value("${fiserv.api-key:}") String apiKey) {
        this.restTemplate = builder.setConnectTimeout(Duration.ofSeconds(5)).setReadTimeout(Duration.ofSeconds(5)).build();
        this.baseUrl = baseUrl == null ? "" : baseUrl;
        this.apiKey = apiKey == null ? "" : apiKey;
    }

    // Helper constructor for tests that want to supply a RestTemplate directly
    public FiservClient(RestTemplate restTemplate, String baseUrl, String apiKey) {
        this.restTemplate = restTemplate;
        this.baseUrl = baseUrl == null ? "" : baseUrl;
        this.apiKey = apiKey == null ? "" : apiKey;
    }

    public double getBalanceByEmail(String email) throws FiservException {
        try {
            String url = baseUrl.endsWith("/") ? baseUrl + "balance" : baseUrl + "/balance";
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            if (!this.apiKey.isEmpty()) {
                headers.set(HttpHeaders.AUTHORIZATION, "Bearer " + this.apiKey);
            }
            HttpEntity<Map<String, String>> entity = new HttpEntity<>(Map.of("email", email), headers);
            ResponseEntity<Map> resp = restTemplate.postForEntity(url, entity, Map.class);
            if (!resp.getStatusCode().is2xxSuccessful() || resp.getBody() == null) {
                throw new FiservException("Invalid response from Fiserv: " + resp.getStatusCode());
            }
            Object bal = resp.getBody().get("balance");
            if (bal == null) throw new FiservException("Missing balance in response");
            return Double.parseDouble(bal.toString());
        } catch (RestClientException e) {
            throw new FiservException("Error contacting Fiserv", e);
        }
    }

    public static class FiservException extends Exception {
        public FiservException(String message) { super(message); }
        public FiservException(String message, Throwable cause) { super(message, cause); }
    }
}
