package com.chewy.order.service;

import com.chewy.order.integration.FedExClient;
import org.springframework.stereotype.Service;

import java.util.Map;

@Service
public class FulfillmentService {

    private final FedExClient client;
    private final OrderService orderService;

    public FulfillmentService(FedExClient client, OrderService orderService) {
        this.client = client;
        this.orderService = orderService;
    }

    public void fulfillOrder(String orderId) {
        Map<String, Object> resp = client.fulfill(orderId);
        if (resp != null && "ACK".equals(resp.get("status"))) {
            String tracking = String.valueOf(resp.get("trackingId"));
            orderService.markFulfilled(orderId, tracking);
        }
    }
}
