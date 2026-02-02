package com.chewy.payment.integration;

public interface FiservService {
    double getBalanceByEmail(String email) throws FiservClient.FiservException;
}
