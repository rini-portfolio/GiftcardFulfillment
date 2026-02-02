"""
Notification Service - SQS Consumer for Payment and Giftcard Notifications
Listens to SQS queues and sends notifications (email, SMS, etc.)
"""

import json
import logging
import os
from typing import Optional
import boto3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import time
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Notification Service", version="1.0.0")

# AWS SQS Configuration
NOTIFICATION_QUEUE_URL = os.environ.get(
    'NOTIFICATION_QUEUE_URL',
    'http://localhost:4566/000000000000/notify-queue'
)
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

# Initialize SQS client
sqs_client = boto3.client(
    'sqs',
    region_name=AWS_REGION,
    endpoint_url=os.environ.get('AWS_ENDPOINT_URL', None),
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID', 'test'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY', 'test')
)


class NotificationMessage(BaseModel):
    """Notification message model"""
    type: str  # 'EMAIL', 'SMS', 'PUSH'
    recipient: str  # email or phone
    subject: Optional[str] = None
    body: str
    data: Optional[dict] = None


class PaymentNotification(BaseModel):
    """Payment event notification"""
    orderId: str
    customerId: str
    status: str  # 'PAID', 'INSUFFICIENT_FUNDS', 'FAILED'
    amount: float
    timestamp: str


class GiftcardNotification(BaseModel):
    """Giftcard issued notification"""
    giftcardId: str
    email: str
    amount: float
    timestamp: str


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "notification-service",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/notify")
def send_notification(message: NotificationMessage) -> dict:
    """
    Send a notification directly (for testing/admin use)
    """
    try:
        logger.info(f"Sending {message.type} notification to {message.recipient}")
        
        # In a real system, this would integrate with email/SMS providers
        # For now, we just log it
        notification_details = {
            "type": message.type,
            "recipient": message.recipient,
            "subject": message.subject,
            "body": message.body,
            "sent_at": datetime.utcnow().isoformat(),
            "status": "sent"
        }
        
        logger.info(f"Notification sent: {notification_details}")
        return notification_details
        
    except Exception as e:
        logger.error(f"Failed to send notification: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process-payment-notification")
def process_payment_notification(notification: PaymentNotification) -> dict:
    """
    Process payment notification and send to customer
    """
    try:
        logger.info(f"Processing payment notification for order {notification.orderId}")
        
        # Determine notification message based on status
        status_messages = {
            "PAID": f"Your payment of ${notification.amount} has been processed successfully.",
            "INSUFFICIENT_FUNDS": f"Payment failed: Insufficient funds. Required: ${notification.amount}",
            "FAILED": f"Payment processing failed. Please try again later."
        }
        
        body = status_messages.get(
            notification.status,
            "Your payment status has been updated."
        )
        
        notification_msg = NotificationMessage(
            type="EMAIL",
            recipient=f"customer-{notification.customerId}@example.com",
            subject=f"Order {notification.orderId} - Payment {notification.status}",
            body=body,
            data={
                "orderId": notification.orderId,
                "status": notification.status,
                "amount": notification.amount
            }
        )
        
        return send_notification(notification_msg)
        
    except Exception as e:
        logger.error(f"Failed to process payment notification: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process-giftcard-notification")
def process_giftcard_notification(notification: GiftcardNotification) -> dict:
    """
    Process giftcard notification and send to customer
    """
    try:
        logger.info(f"Processing giftcard notification for {notification.email}")
        
        body = f"""
Your giftcard has been successfully issued!

Giftcard ID: {notification.giftcardId}
Amount: ${notification.amount}
Issued: {notification.timestamp}

You can now use this giftcard for purchases.
        """.strip()
        
        notification_msg = NotificationMessage(
            type="EMAIL",
            recipient=notification.email,
            subject=f"Your Giftcard {notification.giftcardId} is Ready",
            body=body,
            data={
                "giftcardId": notification.giftcardId,
                "amount": notification.amount
            }
        )
        
        return send_notification(notification_msg)
        
    except Exception as e:
        logger.error(f"Failed to process giftcard notification: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/consume-queue")
def consume_queue_messages(max_messages: int = 10) -> dict:
    """
    Consume messages from SQS queue and process them
    """
    try:
        logger.info(f"Consuming up to {max_messages} messages from queue")
        
        response = sqs_client.receive_message(
            QueueUrl=NOTIFICATION_QUEUE_URL,
            MaxNumberOfMessages=max_messages,
            WaitTimeSeconds=1
        )
        
        messages = response.get('Messages', [])
        processed = 0
        
        for message in messages:
            try:
                body = json.loads(message['Body'])
                logger.info(f"Processing message: {body}")
                
                # Determine message type and process accordingly
                if 'orderId' in body:
                    process_payment_notification(PaymentNotification(**body))
                elif 'giftcardId' in body:
                    process_giftcard_notification(GiftcardNotification(**body))
                
                # Delete message after processing
                sqs_client.delete_message(
                    QueueUrl=NOTIFICATION_QUEUE_URL,
                    ReceiptHandle=message['ReceiptHandle']
                )
                processed += 1
                
            except Exception as e:
                logger.error(f"Failed to process message: {str(e)}")
                # Don't delete, let it retry
        
        return {
            "total_messages": len(messages),
            "processed": processed,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to consume queue: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Background task to continuously consume messages
def start_queue_consumer():
    """Start consuming messages from queue in background"""
    logger.info("Queue consumer started")
    while True:
        try:
            consume_queue_messages()
            time.sleep(5)  # Check queue every 5 seconds
        except Exception as e:
            logger.error(f"Queue consumer error: {str(e)}")
            time.sleep(10)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
