package com.chewy.payment.model;

import java.io.Serializable;
import java.time.LocalDateTime;

public class PaymentEvent implements Serializable {
    private String orderId;
    private String email;
    private double amount;
    private String status;
    private LocalDateTime timestamp;

    // Constructors
    public PaymentEvent() {}

    public PaymentEvent(String orderId, String email, double amount, String status, LocalDateTime timestamp) {
        this.orderId = orderId;
        this.email = email;
        this.amount = amount;
        this.status = status;
        this.timestamp = timestamp;
    }

    // Getters & Setters
    public String getOrderId() { return orderId; }
    public void setOrderId(String orderId) { this.orderId = orderId; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public double getAmount() { return amount; }
    public void setAmount(double amount) { this.amount = amount; }

    public LocalDateTime getTimestamp() { return timestamp; }
    public void setTimestamp(LocalDateTime timestamp) { this.timestamp = timestamp; }
} 
