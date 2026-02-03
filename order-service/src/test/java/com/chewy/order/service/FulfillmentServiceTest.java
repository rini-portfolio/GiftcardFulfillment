package com.chewy.order.service;

import com.chewy.order.integration.FedExClient;
import org.junit.jupiter.api.Test;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

public class FulfillmentServiceTest {

    static class FakeFedExClient extends FedExClient {
        private final Map<String, Object> resp;

        public FakeFedExClient(Map<String, Object> resp) {
            super(new RestTemplate(), "http://localhost:9091/");
            this.resp = resp;
        }

        @Override
        public Map<String, Object> fulfill(String orderId) {
            return resp;
        }
    }

    static class SpyOrderService extends OrderService {
        public String lastOrderId;
        public String lastTracking;

        public SpyOrderService() {
            super(new com.chewy.order.integration.SqsPublisher(null, null), null);
        }

        @Override
        public void markFulfilled(String orderId, String trackingId) {
            this.lastOrderId = orderId;
            this.lastTracking = trackingId;
            // do not call parent persistence in unit test
        }
    }

    @Test
    public void when_ack_then_markFulfilled_called() {
        FakeFedExClient client = new FakeFedExClient(Map.of("status", "ACK", "trackingId", "FDX-ABC"));
        SpyOrderService orderService = new SpyOrderService();

        FulfillmentService service = new FulfillmentService(client, orderService);
        service.fulfillOrder("ORD-1");

        assertEquals("ORD-1", orderService.lastOrderId);
        assertEquals("FDX-ABC", orderService.lastTracking);
    }

    @Test
    public void when_not_ack_then_no_mark() {
        FakeFedExClient client = new FakeFedExClient(Map.of("status", "NACK"));
        SpyOrderService orderService = new SpyOrderService();

        FulfillmentService service = new FulfillmentService(client, orderService);
        service.fulfillOrder("ORD-2");

        assertNull(orderService.lastOrderId);
    }
}
