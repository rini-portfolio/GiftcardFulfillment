package com.chewy.order.controller;

import com.chewy.order.model.OrderEvent;
import com.chewy.order.service.OrderService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/orders")
public class OrderController {

	private final OrderService orderService;

	public OrderController(OrderService orderService) {
		this.orderService = orderService;
	}

	@PostMapping
	public ResponseEntity<Void> createOrder(@RequestBody OrderEvent event) {
		orderService.createOrder(event);
		return ResponseEntity.accepted().build();
	}

}
