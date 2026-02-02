package com.chewy.payment.service;

import com.chewy.payment.integration.FiservService;
import com.chewy.payment.integration.SqsPublisher;
import com.chewy.payment.model.PaymentEvent;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

public class PaymentServiceTest {

    private SqsPublisher publisher;
    private FiservService fiservClient;
    private PaymentService paymentService;

    static class FakePublisher extends SqsPublisher {
        private PaymentEvent last;
        public FakePublisher() {
            super(null, new com.fasterxml.jackson.databind.ObjectMapper(), "queue");
        }
        @Override
        public void publish(PaymentEvent event) {
            this.last = event;
        }
        public PaymentEvent getLast() { return last; }
    }

    static class FakeFiserv implements FiservService {
        double balance = 0;
        boolean throwError = false;
        public void setBalance(double b) { this.balance = b; }
        public void setThrowError(boolean val) { this.throwError = val; }
        @Override
        public double getBalanceByEmail(String email) throws com.chewy.payment.integration.FiservClient.FiservException {
            if (throwError) throw new com.chewy.payment.integration.FiservClient.FiservException("down");
            return balance;
        }
    }

    @BeforeEach
    public void setup() {
        publisher = new FakePublisher();
        FakeFiserv ff = new FakeFiserv();
        fiservClient = ff;
        paymentService = new PaymentService(publisher, fiservClient);
    }

    @Test
    public void process_shouldMarkPaid_whenBalanceSufficient() throws Exception {
        PaymentEvent ev = new PaymentEvent();
        ev.setEmail("a@b.com");
        ev.setAmount(50.0);

        // set fake balance
        ((FakeFiserv)fiservClient).setBalance(100.0);

        PaymentEvent out = paymentService.process(ev);
        assertEquals("PAID", out.getStatus());
        // ensure publisher got the event
        assertNotNull(((FakePublisher)publisher).getLast());
    }

    @Test
    public void process_shouldMarkInsufficient_whenBalanceTooLow() throws Exception {
        PaymentEvent ev = new PaymentEvent();
        ev.setEmail("a@b.com");
        ev.setAmount(200.0);

        ((FakeFiserv)fiservClient).setBalance(100.0);

        PaymentEvent out = paymentService.process(ev);
        assertEquals("INSUFFICIENT_FUNDS", out.getStatus());
        assertNotNull(((FakePublisher)publisher).getLast());
    }

    @Test
    public void process_shouldMarkFailed_whenFiservErrors() throws Exception {
        PaymentEvent ev = new PaymentEvent();
        ev.setEmail("a@b.com");
        ev.setAmount(50.0);

        ((FakeFiserv)fiservClient).setThrowError(true);

        PaymentEvent out = paymentService.process(ev);
        assertEquals("FAILED", out.getStatus());
        assertNotNull(((FakePublisher)publisher).getLast());
    }
}
