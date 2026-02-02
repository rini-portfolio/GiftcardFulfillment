package com.chewy.payment.listener;

import com.chewy.payment.service.PaymentService;
import com.chewy.payment.integration.SqsPublisher;
import com.chewy.payment.model.PaymentEvent;
import org.springframework.stereotype.Component;

@Component
public class PaymentListener {

    private final PaymentService service;
    private final SqsPublisher publisher;

    public PaymentListener(PaymentService service, SqsPublisher publisher) {
        this.service = service;
        this.publisher = publisher;
    }

    public void handle(PaymentEvent event) {
        PaymentEvent paid = service.process(event);
        publisher.publish(paid);
    }
} 