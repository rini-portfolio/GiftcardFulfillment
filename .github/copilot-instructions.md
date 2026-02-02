<!-- Purpose: concise, actionable guidance for AI coding agents working on this repo -->
# Copilot instructions — Order Service (Spring Boot + SQS)

This file contains focused, discoverable knowledge that helps an AI agent be immediately productive in this repository.

- **Big picture:** A small Spring Boot microservice that exposes REST endpoints, applies simple business logic in `OrderService`, and publishes order events to AWS SQS via `SqsPublisher`. Key code lives under `src/main/java/com/chewy/order` and the application entrypoint is `OrderApplication.java`.

- **Key files:**
  - `pom.xml` — Spring Boot 3.2.1 parent, **Java 21** (see `<java.version>`), and `com.amazonaws:aws-java-sdk-sqs`. Build with Maven.
  - `OrderApplication.java` — Spring Boot `@SpringBootApplication` entrypoint.
  - `src/main/java/com/chewy/order/controller/OrderController.java` — REST controller (accepts `OrderEvent` JSON).
  - `src/main/java/com/chewy/order/service/OrderService.java` — business logic layer (forwards events to SQS).
  - `src/main/java/com/chewy/order/integration/SqsPublisher.java` — SQS integration; reads `aws.sqs.order-queue-url`.
  - `src/main/java/com/chewy/order/model/OrderEvent.java` — event DTO (orderId, status, timestamp).
  - `src/main/resources/application.yml` — configuration (currently empty). Prefer placing `aws.sqs.order-queue-url` and `aws.region` here or set via environment variables (Spring Boot relaxed binding maps `AWS_SQS_ORDER_QUEUE_URL`).

- **Project-specific patterns & conventions (explicit):**
  - Package root should be `com.chewy.order`. Several files are currently missing or using incorrect package declarations (e.g., `package model;`, `package service;`, or no `package`). When adding or modifying Java classes, ensure the file's `package` line is `package com.chewy.order.<layer>;` (example: controller, service, integration, model).
  - Annotate Spring components explicitly: `@RestController` for controllers, `@Service` for services, `@Component` or custom config for infra classes. Use constructor injection for dependencies.
  - Configuration values (queue URL, AWS region) should be injected from `application.yml` using `@Value` or a `@ConfigurationProperties` class.
  - Do not add Lombok unless you also add the dependency to `pom.xml` and ensure maintainers approve; prefer plain Java for clarity.

- **Integrations & environment:**
  - SQS integration uses the AWS Java SDK (`aws-java-sdk-sqs`). Use the AWS Default Credentials Provider Chain (env vars, shared credentials file, IAM role) — do not hardcode credentials.
  - Queue URLs and AWS region should come from `application.yml` or environment variables. Example keys: `aws.sqs.orderQueueUrl` and `aws.region`.

- **Build / run / test commands:**
  - Build artifact: `mvn -e -B clean package`
  - Run locally (dev): `mvn spring-boot:run` or `java -jar target/order-service-0.0.1-SNAPSHOT.jar`
  - Tests: `mvn test` (project currently has test dependencies but no tests yet).

- **When editing code, follow these concrete examples:**
  - Correct package declarations. Example header for the controller:

    ```java
    package com.chewy.order.controller;

    import org.springframework.web.bind.annotation.*;

    @RestController
    @RequestMapping("/orders")
    public class OrderController {
        private final OrderService orderService;

        public OrderController(OrderService orderService) {
            this.orderService = orderService;
        }
    }
    ```

    - **Patterns & small implementation notes (discovered from code):**
      - `OrderController#createOrder` accepts `OrderEvent` JSON and returns HTTP 202 (accepted).
      - `OrderService.handle` currently forwards events to `SqsPublisher.publish(event)`.
      - `SqsPublisher.publish` serializes `OrderEvent` via Jackson and calls `AmazonSQS.sendMessage`. It catches Exception and prints a stack trace — consider adding proper logging and retry/poison-queue behavior when changing this.

    - **Editing guidance for AI agents**
      - Keep changes minimal and well-scoped. Validate compilation with: `mvn -q -DskipTests package`.
      - If adding new dependencies (e.g., Lombok), update `pom.xml` and mark for maintainer review.

    - **Where to look for more context:**
      - Controller: `src/main/java/com/chewy/order/controller/OrderController.java`
      - Service: `src/main/java/com/chewy/order/service/OrderService.java`
      - SQS integration: `src/main/java/com/chewy/order/integration/SqsPublisher.java`

    If anything here is unclear or you want more examples (CI steps, local env var examples, or an integration test scaffold), tell me which area to expand.
