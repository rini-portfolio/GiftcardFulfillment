from fastapi import FastAPI, HTTPException
import boto3
import json
import uuid
import os
import logging
import requests

app = FastAPI()
sqs = boto3.client("sqs")
NOTIFY_QUEUE = os.environ.get("NOTIFICATION_QUEUE_URL", "NOTIFICATION_QUEUE_URL")
FISERV_URL = os.environ.get("FISERV_URL")
FISERV_API_KEY = os.environ.get("FISERV_API_KEY")
FISERV_TIMEOUT = int(os.environ.get("FISERV_TIMEOUT", "5"))
FISERV_RETRIES = int(os.environ.get("FISERV_RETRIES", "3"))

# try relative import first to support running as a package/module
try:
    from .fiserv_client import FiservClient, FiservError
except Exception:
    from fiserv_client import FiservClient, FiservError

# instantiate client if configured
fiserv_client = None
if FISERV_URL:
    fiserv_client = FiservClient(FISERV_URL, FISERV_API_KEY, timeout=FISERV_TIMEOUT, retries=FISERV_RETRIES)

logger = logging.getLogger("giftcard-service")
logging.basicConfig(level=logging.INFO)

@app.post("/issue")
def issue_giftcard(event: dict):
    email = event.get("email")
    amount = event.get("amount")
    if not email or amount is None:
        raise HTTPException(status_code=400, detail="Missing email or amount")

    if not fiserv_client:
        raise HTTPException(status_code=500, detail="Fiserv endpoint not configured (FISERV_URL)")

    # Use Fiserv client to issue the gift card
    try:
        giftcard_id = fiserv_client.issue(email, amount)
    except FiservError:
        logger.exception("Error issuing giftcard via Fiserv")
        raise HTTPException(status_code=502, detail="Error contacting Fiserv")

    giftcard = {"giftcardId": giftcard_id, "email": email, "amount": amount}

    # Notify other services via SQS (best-effort)
    try:
        sqs.send_message(QueueUrl=NOTIFY_QUEUE, MessageBody=json.dumps(giftcard))
    except Exception:
        logger.exception("Failed to publish giftcard message to SQS")

    return {"status": "Gift card issued", "giftcard": giftcard}