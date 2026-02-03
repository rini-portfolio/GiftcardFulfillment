package com.chewy.order.integration;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.ResponseEntity;
import java.util.Map;

@Component
public class FedExClient {

    private final RestTemplate restTemplate;
    private final String fulfillmentUrl;

    public FedExClient(RestTemplate restTemplate, @Value("${FULFILLMENT_URL:http://localhost:9091/}") String fulfillmentUrl) {
        this.restTemplate = restTemplate;
        this.fulfillmentUrl = fulfillmentUrl;
    }

    public Map<String, Object> fulfill(String orderId) {
        String url = fulfillmentUrl;
        if (!url.endsWith("/")) url = url + "/";
        url = url + "fulfill";
        ResponseEntity<Map> resp = restTemplate.postForEntity(url, Map.of("orderId", orderId), Map.class);
        return resp.getBody();
    }
}
