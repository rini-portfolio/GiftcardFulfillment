package com.chewy.order.service;

import com.chewy.order.model.Order;
import com.chewy.order.model.OrderEvent;
import com.chewy.order.repository.OrderRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;

import java.time.LocalDateTime;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.mock;

@DataJpaTest
public class OrderServicePersistenceTest {

    @Autowired
    private OrderRepository repository;

    @Test
    public void createOrder_persistsOrderWithCreatedStatus() {
        // avoid Mockito inlining issues by using a simple no-op publisher
        com.chewy.order.integration.SqsPublisher fakePublisher = new com.chewy.order.integration.SqsPublisher(null,
                new com.fasterxml.jackson.databind.ObjectMapper()) {
            @Override
            public void publish(com.chewy.order.model.OrderEvent event) {
                // no-op for tests
            }
        };

        OrderService service = new OrderService(fakePublisher, repository);

        OrderEvent e = new OrderEvent("ORD-100", "CUST-1", 10.0, "CREATED", LocalDateTime.now());
        service.createOrder(e);

        Order o = repository.findById("ORD-100").orElse(null);
        assertNotNull(o);
        assertEquals("CUST-1", o.getCustomerId());
        assertEquals(10.0, o.getAmount().doubleValue());
        assertEquals(com.chewy.order.model.OrderStatus.CREATED, o.getStatus());
    }
}
