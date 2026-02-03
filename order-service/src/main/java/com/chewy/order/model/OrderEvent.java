package com.chewy.order.model;

import java.io.Serializable;
import java.time.LocalDateTime;
import java.math.BigDecimal;

public class OrderEvent implements Serializable {
    private String orderId;
    private String customerId;
    private Double amount;
    private String status; // CREATED, PAID, COMPLETED
    private LocalDateTime timestamp;

    // Constructors
    public OrderEvent() {}

    public OrderEvent(String orderId, String customerId, Double amount, String status, LocalDateTime timestamp) {
        this.orderId = orderId;
        this.customerId = customerId;
        this.amount = amount;
        this.status = status;
        this.timestamp = timestamp;
    }

    // Getters & Setters
    public String getOrderId() { return orderId; }
    public void setOrderId(String orderId) { this.orderId = orderId; }

    public String getCustomerId() { return customerId; }
    public void setCustomerId(String customerId) { this.customerId = customerId; }

    public Double getAmount() { return amount; }
    public void setAmount(Double amount) { this.amount = amount; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public LocalDateTime getTimestamp() { return timestamp; }
    public void setTimestamp(LocalDateTime timestamp) { this.timestamp = timestamp; }
}
