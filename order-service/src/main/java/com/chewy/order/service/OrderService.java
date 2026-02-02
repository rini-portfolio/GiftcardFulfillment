package com.chewy.order.service;

import com.chewy.order.integration.SqsPublisher;
import com.chewy.order.model.OrderEvent;
import org.springframework.stereotype.Service;

@Service
public class OrderService {

	private final SqsPublisher publisher;

	public OrderService(SqsPublisher publisher) {
		this.publisher = publisher;
	}

	public void createOrder(OrderEvent event) {
		// simple business logic stub: publish event to SQS
		publisher.publish(event);
	}

}
