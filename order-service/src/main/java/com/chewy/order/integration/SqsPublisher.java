package com.chewy.order.integration;

import com.chewy.order.model.OrderEvent;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.amazonaws.services.sqs.AmazonSQS;
import com.amazonaws.services.sqs.model.SendMessageRequest;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Component
public class SqsPublisher {

	private final AmazonSQS sqsClient;
    private final ObjectMapper objectMapper;

    @Value("${aws.sqs.order-queue-url}")
    private String orderQueueUrl;

    public SqsPublisher(AmazonSQS sqsClient, ObjectMapper objectMapper) {
        this.sqsClient = sqsClient;
        this.objectMapper = objectMapper;
    }

    public void publish(OrderEvent event) {
        try {
            String messageBody = objectMapper.writeValueAsString(event);
            SendMessageRequest request = new SendMessageRequest()
                    .withQueueUrl(orderQueueUrl)
                    .withMessageBody(messageBody);
            sqsClient.sendMessage(request);
        } catch (Exception e) {
            e.printStackTrace();
            // handle retry or logging here
        }
    }

}
