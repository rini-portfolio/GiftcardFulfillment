#!/usr/bin/env bash
set -euo pipefail

# This script runs inside the LocalStack container at startup (mounted to /etc/localstack/init/ready.d)
# It creates the SQS queues our services expect.

awslocal sqs create-queue --queue-name order-queue
awslocal sqs create-queue --queue-name payment-queue
awslocal sqs create-queue --queue-name notify-queue

# print queue urls for visibility
awslocal sqs get-queue-url --queue-name order-queue
awslocal sqs get-queue-url --queue-name payment-queue
awslocal sqs get-queue-url --queue-name notify-queue
