package com.chewy.payment.integration;

import org.junit.jupiter.api.Test;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.http.MediaType;
import org.springframework.test.web.client.MockRestServiceServer;
import org.springframework.web.client.RestTemplate;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.content;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.header;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.method;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.requestTo;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withSuccess;
import static org.springframework.http.HttpMethod.POST;

public class FiservClientTest {

    @Test
    public void getBalanceByEmail_success() throws Exception {
        RestTemplate restTemplate = new RestTemplate();
        MockRestServiceServer mockServer = MockRestServiceServer.createServer(restTemplate);

        String url = "http://fiserv.test/balance";
        mockServer.expect(requestTo(url))
                .andExpect(method(POST))
                .andRespond(withSuccess("{\"balance\": 150.5}", MediaType.APPLICATION_JSON));

        // instantiate a client but inject the restTemplate directly
        FiservClient client = new FiservClient(restTemplate, "http://fiserv.test", "");
        double bal = client.getBalanceByEmail("a@b.com");
        assertEquals(150.5, bal, 0.001);

        mockServer.verify();
    }
}
