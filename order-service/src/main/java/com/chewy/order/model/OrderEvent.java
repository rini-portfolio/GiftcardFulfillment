package com.chewy.order.model;

import java.io.Serializable;
import java.time.LocalDateTime;

public class OrderEvent implements Serializable {
    private String orderId;
    private String status; // CREATED, PAID, COMPLETED
    private LocalDateTime timestamp;

    // Constructors
    public OrderEvent() {}

    public OrderEvent(String orderId, String status, LocalDateTime timestamp) {
        this.orderId = orderId;
        this.status = status;
        this.timestamp = timestamp;
    }

    // Getters & Setters
    public String getOrderId() { return orderId; }
    public void setOrderId(String orderId) { this.orderId = orderId; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public LocalDateTime getTimestamp() { return timestamp; }
    public void setTimestamp(LocalDateTime timestamp) { this.timestamp = timestamp; }
}
