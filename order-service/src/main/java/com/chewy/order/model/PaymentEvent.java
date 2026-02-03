package com.chewy.order.model;

import java.math.BigDecimal;

public class PaymentEvent {
    private String orderId;
    private String status;
    private BigDecimal amount;

    public PaymentEvent() {}

    public String getOrderId() { return orderId; }
    public void setOrderId(String orderId) { this.orderId = orderId; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public BigDecimal getAmount() { return amount; }
    public void setAmount(BigDecimal amount) { this.amount = amount; }
}
