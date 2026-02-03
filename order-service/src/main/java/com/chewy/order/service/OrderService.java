package com.chewy.order.service;

import com.chewy.order.integration.SqsPublisher;
import com.chewy.order.model.OrderEvent;
import com.chewy.order.model.Order;
import com.chewy.order.model.OrderStatus;
import com.chewy.order.repository.OrderRepository;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;

@Service
public class OrderService {

    private final SqsPublisher publisher;
    private final OrderRepository orderRepository;

    public OrderService(SqsPublisher publisher, OrderRepository orderRepository) {
        this.publisher = publisher;
        this.orderRepository = orderRepository;
    }

    public void createOrder(OrderEvent event) {
        // persist order in CREATED state
        Order order = new Order(event.getOrderId(), event.getCustomerId(), BigDecimal.valueOf(event.getAmount()), OrderStatus.CREATED);
        orderRepository.save(order);

        // publish event to SQS
        publisher.publish(event);
    }

    public void markPaid(String orderId) {
        orderRepository.findById(orderId).ifPresent(o -> {
            o.setStatus(OrderStatus.PAID);
            orderRepository.save(o);
        });
    }

    public void markFulfilled(String orderId, String trackingId) {
        orderRepository.findById(orderId).ifPresent(o -> {
            o.setStatus(OrderStatus.FULFILLED);
            o.setTrackingId(trackingId);
            orderRepository.save(o);
        });
    }

    public Order getOrder(String orderId) {
        return orderRepository.findById(orderId).orElse(null);
    }

}
