package com.chewy.payment.integration;

import com.amazonaws.services.sqs.AmazonSQS;
import com.amazonaws.services.sqs.model.SendMessageRequest;
import com.chewy.payment.model.PaymentEvent;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Component
public class SqsPublisher {

    private final AmazonSQS sqs;
    private final ObjectMapper mapper;
    private final String queueUrl;

    public SqsPublisher(AmazonSQS sqs, ObjectMapper mapper, @Value("${aws.sqs.payment-queue-url}") String queueUrl) {
        this.sqs = sqs;
        this.mapper = mapper;
        this.queueUrl = queueUrl;
    }

    public void publish(PaymentEvent event) {
        try {
            sqs.sendMessage(new SendMessageRequest()
                    .withQueueUrl(queueUrl)
                    .withMessageBody(mapper.writeValueAsString(event)));
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
} 