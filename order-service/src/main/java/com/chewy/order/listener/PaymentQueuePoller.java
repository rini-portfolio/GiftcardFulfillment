package com.chewy.order.listener;

import com.amazonaws.services.sqs.AmazonSQS;
import com.amazonaws.services.sqs.model.DeleteMessageRequest;
import com.amazonaws.services.sqs.model.ReceiveMessageRequest;
import com.amazonaws.services.sqs.model.Message;
import com.chewy.order.model.PaymentEvent;
import com.chewy.order.service.OrderService;
import com.chewy.order.service.FulfillmentService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.core.env.Environment;
import org.springframework.stereotype.Component;

import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import java.util.concurrent.Executors;
import java.util.concurrent.ExecutorService;
import java.util.List;

@Component
public class PaymentQueuePoller {

    private final AmazonSQS sqs;
    private final Environment env;
    private final ObjectMapper mapper;
    private final OrderService orderService;
    private final FulfillmentService fulfillmentService;
    private final ExecutorService executor = Executors.newSingleThreadExecutor();
    private volatile boolean running = true;

    public PaymentQueuePoller(AmazonSQS sqs, Environment env, ObjectMapper mapper, OrderService orderService, FulfillmentService fulfillmentService) {
        this.sqs = sqs;
        this.env = env;
        this.mapper = mapper;
        this.orderService = orderService;
        this.fulfillmentService = fulfillmentService;
    }

    @PostConstruct
    public void start() {
        executor.submit(this::pollLoop);
    }

    @PreDestroy
    public void stop() {
        running = false;
        executor.shutdownNow();
    }

    private void pollLoop() {
        String queueUrl = env.getProperty("aws.sqs.payment-queue-url");
        if (queueUrl == null || queueUrl.isEmpty()) return;

        ReceiveMessageRequest req = new ReceiveMessageRequest(queueUrl).withWaitTimeSeconds(10).withMaxNumberOfMessages(5);

        while (running) {
            try {
                List<Message> messages = sqs.receiveMessage(req).getMessages();
                for (Message m : messages) {
                    try {
                        PaymentEvent event = mapper.readValue(m.getBody(), PaymentEvent.class);
                        handle(event);
                        sqs.deleteMessage(new DeleteMessageRequest(queueUrl, m.getReceiptHandle()));
                    } catch (Exception e) {
                        // log and continue
                        e.printStackTrace();
                    }
                }
            } catch (Exception e) {
                e.printStackTrace();
                try { Thread.sleep(2000); } catch (InterruptedException ignored) {}
            }
        }
    }

    private void handle(PaymentEvent event) {
        if (event == null || event.getOrderId() == null) return;
        if ("PAID".equalsIgnoreCase(event.getStatus())) {
            orderService.markPaid(event.getOrderId());
            fulfillmentService.fulfillOrder(event.getOrderId());
        } else if ("INSUFFICIENT_FUNDS".equalsIgnoreCase(event.getStatus()) || "FAILED".equalsIgnoreCase(event.getStatus())) {
            // mark failed
            // optional: implement retry/reconciliation
        }
    }
}
