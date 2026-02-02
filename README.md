# Giftcard Fulfillment Platform

A microservices-based giftcard fulfillment platform built with Spring Boot, Python FastAPI, and AWS SQS, featuring third-party Fiserv integration for balance validation and giftcard issuance.

## Case Study — Gift Card Purchase & Fulfillment Flow

Designed scalable microservices architecture with API contracts and deployment automation.

**Tech:** Java, Python, Spring Boot, Docker, Kubernetes, AWS

**View Case Study:** https://github.com/rini-portfolio/techportfolio/blob/main/case_studies/giftcard_purchase_fulfillment.md

## 📋 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Application                      │
└────────────┬────────────────────────────────────┬────────────┘
             │                                    │
      POST /orders                         POST /issue
             │                                    │
    ┌────────▼──────────┐             ┌──────────▼──────────┐
    │  Order Service    │             │ Giftcard Service    │
    │  (Spring Boot)    │             │  (FastAPI Python)   │
    │  Port: 8080       │             │  Port: 8000         │
    └────────┬──────────┘             └──────────┬──────────┘
             │                                    │
             │ OrderEvent                         │ Notification
             │ (SQS)                              │ (SQS)
             ▼                                    │
    ┌────────────────────┐                       │
    │  AWS SQS           │◄──────────────────────┘
    │  (LocalStack)      │
    │  Port: 4566        │
    └────┬─────────┬─────┘
         │         │
    order-queue  notify-queue
         │         │
         ▼         ▼
    ┌──────────────┐      ┌──────────────────┐
    │ Payment      │      │ Notification     │
    │ Service      │      │ Service          │
    │ (Spring Boot)│      │ (FastAPI Python) │
    │ Port: 8081   │      │ Port: 8002       │
    │              │      │                  │
    │ ┌──────────┐ │      │ Sends emails,    │
    │ │FiservAPI │ │      │ SMS, push        │
    │ │(Balance) │ │      │ notifications    │
    │ └──────────┘ │      │                  │
    └──────────────┘      └──────────────────┘

    ┌──────────────────┐
    │  Fiserv API      │
    │  (External)      │
    │  Mock: :9090     │
    └──────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Java 21 (optional, for local development)
- Maven 3.6+ (optional)
- Python 3.11+ (optional)

### Run Everything with Docker Compose

```bash
# From repository root
docker-compose up
```

This will start:
- **LocalStack** (SQS emulation) on http://localhost:4566
- **Mock Fiserv** server on http://localhost:9090
- **Order Service** on http://localhost:8080
- **Payment Service** on http://localhost:8081
- **Giftcard Service** on http://localhost:8000
- **Notification Service** on http://localhost:8002

### Example API Calls

#### 1. Create an Order (Order Service)
```bash
curl -X POST http://localhost:8080/orders \
  -H "Content-Type: application/json" \
  -d '{
    "orderId": "ORD-001",
    "customerId": "CUST-001",
    "amount": 100.00,
    "timestamp": "2026-02-02T09:00:00Z"
  }'
```

Expected Response: HTTP 202 Accepted

#### 2. Issue a Giftcard (Giftcard Service)
```bash
curl -X POST http://localhost:8000/issue \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "amount": 50.00
  }'
```

Expected Response:
```json
{
  "giftcardId": "GC-XXXX-YYYY-ZZZZ",
  "amount": 50.00,
  "email": "customer@example.com"
}
```

#### 3. Check Fiserv Balance (via Payment Service)
The Payment Service automatically queries Fiserv when processing orders. The mock Fiserv always returns a balance of $1000.

---

## 📁 Project Structure

```
giftcard-fulfillment-platform/
├── order-service/                    # Spring Boot REST API
│   ├── src/main/java/com/chewy/order/
│   │   ├── OrderApplication.java
│   │   ├── controller/
│   │   │   └── OrderController.java
│   │   ├── service/
│   │   │   └── OrderService.java
│   │   ├── integration/
│   │   │   └── SqsPublisher.java
│   │   ├── configuration/
│   │   │   └── SqsConfig.java
│   │   └── model/
│   │       └── OrderEvent.java
│   ├── src/main/resources/
│   │   └── application.yml
│   ├── pom.xml
│   └── Dockerfile
│
├── payment-service/                  # Spring Boot SQS Consumer + Fiserv Integration
│   ├── src/main/java/com/chewy/payment/
│   │   ├── PaymentApplication.java
│   │   ├── service/
│   │   │   └── PaymentService.java
│   │   ├── integration/
│   │   │   ├── SqsConfig.java
│   │   │   ├── SqsPublisher.java
│   │   │   ├── FiservClient.java
│   │   │   └── FiservService.java (interface)
│   │   ├── model/
│   │   │   └── PaymentEvent.java
│   ├── src/test/java/com/chewy/payment/
│   │   ├── service/PaymentServiceTest.java
│   │   └── integration/FiservClientTest.java
│   ├── pom.xml
│   └── Dockerfile
│
├── giftcard-service/                 # FastAPI + Fiserv Integration
│   ├── app.py                        # FastAPI application
│   ├── fiserv_client.py             # Fiserv REST client
│   ├── mock_fiserv.py               # Mock Fiserv server for testing
│   ├── requirements.txt
│   ├── tests/
│   │   ├── test_fiserv_client.py
│   │   ├── test_app_issue.py
│   │   └── test_integration.py
│   ├── scripts/
│   │   ├── start.sh
│   │   └── docker-run.sh
│   ├── Dockerfile
│   └── .dockerignore
│
├── notification-service/             # FastAPI SQS Consumer
│   ├── app.py                        # FastAPI application
│   ├── requirements.txt
│   ├── tests.py                      # Unit tests
│   ├── Dockerfile
│   └── .dockerignore
│
├── localstack/
│   └── init/
│       └── create_queues.sh          # LocalStack initialization script
│
├── docker-compose.yml                 # Full stack orchestration
├── INTEGRATION_SUMMARY.md            # Detailed integration status
└── README.md                         # This file
```

---

## 🔨 Building Services Locally

### Build Order Service
```bash
cd order-service
mvn -DskipTests package
```

### Build Payment Service (with Tests)
```bash
cd payment-service
mvn clean package
# Or run tests only:
mvn test
```

### Test Python Giftcard Service
```bash
cd giftcard-service
pip install -r requirements.txt
pytest
```

### Build & Test All (Makefile)
We provide a top-level Makefile to orchestrate Java and Python modules together. From the repository root you can:

```bash
# Build Java and run Python tests (non-blocking for missing pip)
make all

# Run full test suite (Java + Python)
make test

# Quick wrapper script
./scripts/build_all.sh
```

> Tip: Use `make test` in CI (or see `.github/workflows/ci-build.yml`) to run a single command that builds and tests the entire repo.

---

## ⚙️ Configuration

### Environment Variables

All services support the following AWS configuration:
```
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
```

#### Order Service
```
AWS_SQS_ORDER_QUEUE_URL=http://localhost:4566/000000000000/order-queue
```

#### Payment Service
```
AWS_SQS_PAYMENT_QUEUE_URL=http://localhost:4566/000000000000/payment-queue
FISERV_URL=http://localhost:9090/
FISERV_TIMEOUT=5000
```

#### Giftcard Service
```
NOTIFICATION_QUEUE_URL=http://localhost:4566/000000000000/notify-queue
FISERV_URL=http://localhost:9090/
```

---

## 🧪 Testing

### Unit Tests - Payment Service
The payment-service includes comprehensive unit tests:

```bash
cd payment-service
mvn test
```

Results:
- ✅ FiservClientTest (1 test)
- ✅ PaymentServiceTest (3 tests)
- **All tests passing** - Uses fake implementations to avoid test infrastructure compatibility issues

### Unit Tests - Giftcard Service
```
cd giftcard-service
pip install -r requirements.txt
pytest
```

### Unit Tests - Notification Service
```bash
cd notification-service
pip install -r requirements.txt
pytest tests.py
```

Results:
- Comprehensive unit tests for notification processing
- Payment and giftcard notification handling tests
- SQS queue consumption tests
- Mock-based testing to avoid external dependencies

### Integration Tests
Run the full stack with Docker Compose and execute a test flow:

```bash
docker-compose up -d
sleep 10  # Wait for services to start

# Test order creation
curl -X POST http://localhost:8080/orders \
  -H "Content-Type: application/json" \
  -d '{"orderId":"ORD-001","customerId":"CUST-001","amount":100.00,"timestamp":"2026-02-02T09:00:00Z"}'

# Test giftcard issuance
curl -X POST http://localhost:8000/issue \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","amount":50.00}'

docker-compose down
```

---

## 🔍 Fiserv Integration

### How It Works

**Java (Payment Service)**
```
OrderEvent (from SQS)
    ↓
PaymentService.process()
    ↓
FiservClient.getBalanceByEmail(email)
    ↓
REST GET /balance?email=... (to Fiserv)
    ↓
Set PaymentEvent status based on balance:
  • PAID (if balance >= amount)
  • INSUFFICIENT_FUNDS (if balance < amount)
  • FAILED (if error)
    ↓
SqsPublisher.publish(event)
```

**Python (Giftcard Service)**
```
POST /issue {email, amount}
    ↓
FiservClient.issue(email, amount)
    ↓
REST POST /issue (to Fiserv)
    ↓
Returns giftcardId
    ↓
Publish SQS notification
    ↓
Return giftcardId to client
```

### Mock Fiserv Server
For local development, a mock Fiserv server is included in `giftcard-service/mock_fiserv.py`:

- **Balance Endpoint:** `GET /balance?email=...` → returns $1000.00
- **Issue Endpoint:** `POST /issue` → returns random giftcardId
- **Port:** 9090

To use the actual Fiserv API, update the `FISERV_URL` environment variable.

---

## 📊 Data Flow Example

```
1. Client creates order
   POST /orders (Order Service)
   
2. Order Service publishes OrderEvent to SQS
   Queue: order-queue
   
3. Payment Service consumes OrderEvent
   Calls Fiserv API to check customer balance
   Sets status: PAID / INSUFFICIENT_FUNDS / FAILED
   
4. Payment Service publishes PaymentEvent to SQS
   Queue: payment-queue
   
5. Notification Service consumes PaymentEvent
   Sends notification to customer
   
In parallel:
6. Client requests giftcard
   POST /issue (Giftcard Service)
   
7. Giftcard Service calls Fiserv API
   Issues giftcard
   Gets giftcardId
   
8. Giftcard Service publishes notification to SQS
   Queue: notify-queue
   
9. Returns giftcardId to client
```

---

## 🐳 Docker Images

All services include Dockerfiles for containerization:

```bash
# Build images manually
docker build -t order-service:local ./order-service
docker build -t payment-service:local ./payment-service
docker build -t giftcard-service:local ./giftcard-service
```

Or use docker-compose which builds automatically:
```bash
docker-compose up --build
```

---

## 📝 CI/CD

### GitHub Actions
The repository includes a GitHub Actions workflow (`.github/workflows/python-tests.yml`) that:
- Runs on push and pull requests
- Tests Python 3.11
- Installs dependencies
- Runs pytest for giftcard-service

To add Java tests to CI:
```yaml
- name: Run Java Tests
  run: |
    cd payment-service
    mvn test
    cd ../order-service
    mvn test
```

---

## 🚨 Troubleshooting

### Issue: Connection refused when accessing services
**Solution:** Ensure docker-compose is running and services are fully started (wait 10-15 seconds)

### Issue: "No qualifying bean of type 'AmazonSQS'"
**Solution:** Verify `SqsConfig.java` exists and is properly packaged in `com.chewy.order.configuration`

### Issue: Fiserv timeout errors
**Solution:** Check that mock-fiserv container is running or configure FISERV_URL to actual endpoint

### Issue: SQS queue not found
**Solution:** Ensure LocalStack initialization script ran: `docker logs localstack` should show queue creation

### Issue: Payment Service tests fail with Byte Buddy errors
**Solution:** Tests use fake implementations instead of inline mocks to ensure compatibility across Java versions

---

## 📚 Additional Documentation

- [INTEGRATION_SUMMARY.md](INTEGRATION_SUMMARY.md) — Comprehensive integration status and implementation details
- [Copilot Instructions](.github/copilot-instructions.md) — Development guidelines
- Individual service READMEs in each service directory

---

## 🎯 Key Features

✅ **Microservices Architecture** — Independent, scalable services  
✅ **AWS SQS Integration** — Event-driven communication  
✅ **Third-Party API Integration** — Fiserv balance checks and giftcard issuance  
✅ **Comprehensive Testing** — Unit tests for critical components  
✅ **Local Development** — Docker Compose for full-stack local testing  
✅ **CI/CD Ready** — GitHub Actions workflow included  
✅ **Error Handling** — Graceful degradation and error mapping  
✅ **Containerized** — All services include Dockerfiles  

---

## 👥 Development

### Making Changes

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd giftcard-fulfillment-platform
   ```

2. **Start local environment**
   ```bash
   docker-compose up
   ```

3. **Make your changes** in the respective service

4. **Test your changes**
   ```bash
   # For Java services
   cd order-service && mvn test
   cd payment-service && mvn test
   
   # For Python services
   cd giftcard-service && pytest
   ```

5. **Verify builds**
   ```bash
   mvn -q -DskipTests package
   ```

6. **Commit and push**

---

## 📄 License

[Add your license information here]

---

**Last Updated:** 2026-02-02  
**Version:** 1.0.0  
**Status:** Production Ready ✅
