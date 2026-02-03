package com.chewy.order.integration;

import org.junit.jupiter.api.Test;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.test.web.client.MockRestServiceServer;
import org.springframework.test.web.client.match.MockRestRequestMatchers;
import org.springframework.test.web.client.response.MockRestResponseCreators;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

public class FedExClientTest {

    @Test
    public void fulfill_returnsAckAndTracking() {
        RestTemplate rest = new RestTemplate();
        MockRestServiceServer server = MockRestServiceServer.createServer(rest);

        server.expect(MockRestRequestMatchers.requestTo("http://localhost:9091/fulfill"))
                .andExpect(MockRestRequestMatchers.method(HttpMethod.POST))
                .andRespond(MockRestResponseCreators.withSuccess("{\"status\":\"ACK\",\"trackingId\":\"FDX-123\"}", MediaType.APPLICATION_JSON));

        FedExClient client = new FedExClient(rest, "http://localhost:9091/");
        Map<String, Object> resp = client.fulfill("ORD-1");

        assertNotNull(resp);
        assertEquals("ACK", resp.get("status"));
        assertEquals("FDX-123", resp.get("trackingId"));

        server.verify();
    }
}
