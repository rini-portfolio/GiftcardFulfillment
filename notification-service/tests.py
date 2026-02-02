"""
Notification Service tests - Unit and integration tests
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from app import app, NotificationMessage, PaymentNotification, GiftcardNotification


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def mock_sqs():
    """Mock SQS client"""
    with patch('app.sqs_client') as mock:
        yield mock


class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_health_check_returns_200(self, client):
        """Health check should return 200"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert response.json()["service"] == "notification-service"
    
    def test_health_check_has_timestamp(self, client):
        """Health check should include timestamp"""
        response = client.get("/health")
        assert "timestamp" in response.json()


class TestNotifications:
    """Test notification sending"""
    
    def test_send_email_notification(self, client):
        """Should send email notification"""
        message = NotificationMessage(
            type="EMAIL",
            recipient="user@example.com",
            subject="Test Subject",
            body="Test message body"
        )
        response = client.post("/notify", json=message.dict())
        assert response.status_code == 200
        assert response.json()["status"] == "sent"
        assert response.json()["recipient"] == "user@example.com"
    
    def test_send_sms_notification(self, client):
        """Should send SMS notification"""
        message = NotificationMessage(
            type="SMS",
            recipient="+1234567890",
            body="Test SMS message"
        )
        response = client.post("/notify", json=message.dict())
        assert response.status_code == 200
        assert response.json()["status"] == "sent"
    
    def test_notification_includes_data(self, client):
        """Notification should include optional data"""
        message = NotificationMessage(
            type="EMAIL",
            recipient="user@example.com",
            subject="Test",
            body="Test",
            data={"order_id": "ORD-123"}
        )
        response = client.post("/notify", json=message.dict())
        assert response.status_code == 200


class TestPaymentNotifications:
    """Test payment notification processing"""
    
    def test_process_payment_paid_status(self, client):
        """Should process PAID payment notification"""
        notification = PaymentNotification(
            orderId="ORD-001",
            customerId="CUST-001",
            status="PAID",
            amount=100.00,
            timestamp="2026-02-02T09:00:00Z"
        )
        response = client.post(
            "/process-payment-notification",
            json=notification.dict()
        )
        assert response.status_code == 200
        assert "successfully" in response.json()["body"].lower()
    
    def test_process_payment_insufficient_funds(self, client):
        """Should process INSUFFICIENT_FUNDS payment notification"""
        notification = PaymentNotification(
            orderId="ORD-002",
            customerId="CUST-002",
            status="INSUFFICIENT_FUNDS",
            amount=50.00,
            timestamp="2026-02-02T09:00:00Z"
        )
        response = client.post(
            "/process-payment-notification",
            json=notification.dict()
        )
        assert response.status_code == 200
        assert "insufficient" in response.json()["body"].lower()
    
    def test_process_payment_failed_status(self, client):
        """Should process FAILED payment notification"""
        notification = PaymentNotification(
            orderId="ORD-003",
            customerId="CUST-003",
            status="FAILED",
            amount=75.00,
            timestamp="2026-02-02T09:00:00Z"
        )
        response = client.post(
            "/process-payment-notification",
            json=notification.dict()
        )
        assert response.status_code == 200
        assert "failed" in response.json()["body"].lower()
    
    def test_payment_notification_includes_order_data(self, client):
        """Payment notification should include order details"""
        notification = PaymentNotification(
            orderId="ORD-123",
            customerId="CUST-123",
            status="PAID",
            amount=200.00,
            timestamp="2026-02-02T09:00:00Z"
        )
        response = client.post(
            "/process-payment-notification",
            json=notification.dict()
        )
        assert response.status_code == 200
        data = response.json()
        assert "ORD-123" in data["subject"]


class TestGiftcardNotifications:
    """Test giftcard notification processing"""
    
    def test_process_giftcard_notification(self, client):
        """Should process giftcard notification"""
        notification = GiftcardNotification(
            giftcardId="GC-XXXX-YYYY-ZZZZ",
            email="customer@example.com",
            amount=50.00,
            timestamp="2026-02-02T09:00:00Z"
        )
        response = client.post(
            "/process-giftcard-notification",
            json=notification.dict()
        )
        assert response.status_code == 200
        assert "giftcard" in response.json()["body"].lower()
    
    def test_giftcard_notification_has_giftcard_id(self, client):
        """Giftcard notification should include giftcard ID"""
        notification = GiftcardNotification(
            giftcardId="GC-ABC-DEF-123",
            email="user@example.com",
            amount=100.00,
            timestamp="2026-02-02T09:00:00Z"
        )
        response = client.post(
            "/process-giftcard-notification",
            json=notification.dict()
        )
        assert response.status_code == 200
        assert "GC-ABC-DEF-123" in response.json()["body"]
    
    def test_giftcard_notification_recipient(self, client):
        """Giftcard notification should be sent to correct email"""
        notification = GiftcardNotification(
            giftcardId="GC-123",
            email="test@example.com",
            amount=50.00,
            timestamp="2026-02-02T09:00:00Z"
        )
        response = client.post(
            "/process-giftcard-notification",
            json=notification.dict()
        )
        assert response.status_code == 200
        assert response.json()["recipient"] == "test@example.com"


class TestQueueConsumer:
    """Test SQS queue consumption"""
    
    def test_consume_queue_messages(self, client, mock_sqs):
        """Should consume messages from queue"""
        mock_sqs.receive_message.return_value = {
            'Messages': []
        }
        
        response = client.post("/consume-queue")
        assert response.status_code == 200
        assert response.json()["total_messages"] == 0
        assert response.json()["processed"] == 0
    
    def test_consume_queue_with_payment_message(self, client, mock_sqs):
        """Should process payment message from queue"""
        mock_sqs.receive_message.return_value = {
            'Messages': [
                {
                    'Body': json.dumps({
                        'orderId': 'ORD-001',
                        'customerId': 'CUST-001',
                        'status': 'PAID',
                        'amount': 100.00,
                        'timestamp': '2026-02-02T09:00:00Z'
                    }),
                    'ReceiptHandle': 'receipt-123'
                }
            ]
        }
        
        response = client.post("/consume-queue")
        assert response.status_code == 200
        assert response.json()["total_messages"] == 1
    
    def test_consume_queue_with_giftcard_message(self, client, mock_sqs):
        """Should process giftcard message from queue"""
        mock_sqs.receive_message.return_value = {
            'Messages': [
                {
                    'Body': json.dumps({
                        'giftcardId': 'GC-123',
                        'email': 'user@example.com',
                        'amount': 50.00,
                        'timestamp': '2026-02-02T09:00:00Z'
                    }),
                    'ReceiptHandle': 'receipt-456'
                }
            ]
        }
        
        response = client.post("/consume-queue")
        assert response.status_code == 200
        assert response.json()["total_messages"] == 1
    
    def test_consume_queue_deletes_processed_messages(self, client, mock_sqs):
        """Should delete messages after processing"""
        mock_sqs.receive_message.return_value = {
            'Messages': [
                {
                    'Body': json.dumps({
                        'orderId': 'ORD-001',
                        'customerId': 'CUST-001',
                        'status': 'PAID',
                        'amount': 100.00,
                        'timestamp': '2026-02-02T09:00:00Z'
                    }),
                    'ReceiptHandle': 'receipt-123'
                }
            ]
        }
        
        response = client.post("/consume-queue")
        assert response.status_code == 200
        
        # Verify delete_message was called
        mock_sqs.delete_message.assert_called_once()


class TestNotificationModels:
    """Test notification data models"""
    
    def test_notification_message_model(self):
        """Should create notification message"""
        msg = NotificationMessage(
            type="EMAIL",
            recipient="user@example.com",
            subject="Test",
            body="Test body"
        )
        assert msg.type == "EMAIL"
        assert msg.recipient == "user@example.com"
    
    def test_payment_notification_model(self):
        """Should create payment notification"""
        notification = PaymentNotification(
            orderId="ORD-001",
            customerId="CUST-001",
            status="PAID",
            amount=100.00,
            timestamp="2026-02-02T09:00:00Z"
        )
        assert notification.orderId == "ORD-001"
        assert notification.status == "PAID"
    
    def test_giftcard_notification_model(self):
        """Should create giftcard notification"""
        notification = GiftcardNotification(
            giftcardId="GC-123",
            email="user@example.com",
            amount=50.00,
            timestamp="2026-02-02T09:00:00Z"
        )
        assert notification.giftcardId == "GC-123"
        assert notification.email == "user@example.com"


import json
