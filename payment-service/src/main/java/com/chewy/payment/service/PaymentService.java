package com.chewy.payment.service;

import com.chewy.payment.integration.FiservService;
import com.chewy.payment.integration.SqsPublisher;
import com.chewy.payment.model.PaymentEvent;
import org.springframework.stereotype.Service;

@Service
public class PaymentService {

    private final SqsPublisher publisher;
    private final FiservService fiservClient;

    public PaymentService(SqsPublisher publisher, FiservService fiservClient) {
        this.publisher = publisher;
        this.fiservClient = fiservClient;
    }

    public PaymentEvent process(PaymentEvent event) {
        // Check balance via Fiserv
        try {
            double balance = fiservClient.getBalanceByEmail(event.getEmail());
            if (balance >= event.getAmount()) {
                event.setStatus("PAID");
            } else {
                event.setStatus("INSUFFICIENT_FUNDS");
            }
        } catch (Exception e) {
            // If Fiserv call fails, mark as FAILED
            event.setStatus("FAILED");
        }

        // publish event to SQS (best-effort)
        try {
            publisher.publish(event);
        } catch (Exception e) {
            // log or handle publishing failure; keep event status as is
            e.printStackTrace();
        }

        return event;
    }

} 
