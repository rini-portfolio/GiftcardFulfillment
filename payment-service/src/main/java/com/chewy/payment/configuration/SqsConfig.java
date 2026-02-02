package com.chewy.payment.configuration;

import com.amazonaws.services.sqs.AmazonSQS;
import com.amazonaws.services.sqs.AmazonSQSClientBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.env.Environment;

@Configuration
public class SqsConfig {
    @Bean
    public AmazonSQS amazonSqs(Environment env) {
        String region = env.getProperty("aws.region", "us-east-1");
        return AmazonSQSClientBuilder.standard().withRegion(region).build();
    }
} 
