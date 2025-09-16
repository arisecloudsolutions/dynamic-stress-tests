# CI/CD Integration Guide

This guide provides comprehensive instructions for integrating the Dynamic Stress Testing Framework into CI/CD pipelines, with detailed examples for AWS Fargate deployment and homologation environment testing.

## Overview

The framework is designed for seamless integration into modern CI/CD workflows, providing automated load testing as part of your deployment pipeline. This ensures that performance validation occurs consistently across all environment deployments.

## CI/CD Integration Principles

### 1. **Environment-Specific Testing**
- **Development**: Basic functionality and integration testing
- **Staging**: Comprehensive load testing with production-like data
- **Homologation**: Production-equivalent testing before release
- **Production**: Monitoring and validation testing

### 2. **Automated Quality Gates**
- Performance thresholds as deployment gates
- Automatic rollback on performance regression
- Comprehensive reporting and alerting
- Integration with deployment tools

### 3. **Safety-First Approach**
- Conservative load settings for production environments
- Graduated testing intensity across environments
- Automated safety checks and validation
- Emergency stop capabilities

## GitHub Actions Integration

### Basic Workflow

```yaml
name: API Load Testing

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}/load-tester

jobs:
  load-test-staging:
    name: Staging Load Tests
    runs-on: ubuntu-latest
    environment: staging

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Setup Docker Buildx
      uses: docker/setup-buildx-action@v3

    - name: Login to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: Build and push load tester image
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

    - name: Run Load Tests on Staging
      run: |
        docker run --rm \
          -e OPENAPI_URL=${{ secrets.STAGING_OPENAPI_URL }} \
          -e BASE_URL=${{ secrets.STAGING_BASE_URL }} \
          -e AUTH_MODE=jwt \
          -e JWT_TOKEN=${{ secrets.STAGING_JWT_TOKEN }} \
          -e MAX_USERS=25 \
          -e SPAWN_RATE=3 \
          -e RUN_TIME=10m \
          -e SPEC_INCLUDE_TAGS=public,core \
          -e HEADLESS=true \
          -v ${{ github.workspace }}/reports:/app/reports \
          ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}

    - name: Upload Test Reports
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: load-test-reports-staging
        path: reports/
        retention-days: 30

    - name: Performance Gate Check
      run: |
        # Check if average response time is acceptable
        python3 scripts/performance_gate.py \
          --report reports/report.html \
          --max-avg-response-time 500 \
          --max-error-rate 1.0 \
          --min-rps 10

  load-test-homologation:
    name: Homologation Environment Tests
    runs-on: ubuntu-latest
    needs: load-test-staging
    if: github.ref == 'refs/heads/main'
    environment: homologation

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Deploy to AWS Fargate for Testing
      run: |
        # Deploy load testing container to Fargate
        aws ecs run-task \
          --cluster ${{ secrets.FARGATE_CLUSTER }} \
          --task-definition load-testing-task \
          --launch-type FARGATE \
          --network-configuration "awsvpcConfiguration={subnets=[${{ secrets.SUBNET_IDS }}],securityGroups=[${{ secrets.SECURITY_GROUP_ID }}],assignPublicIp=ENABLED}" \
          --overrides '{
            "containerOverrides": [{
              "name": "load-tester",
              "environment": [
                {"name": "OPENAPI_URL", "value": "${{ secrets.HOMOLOG_OPENAPI_URL }}"},
                {"name": "BASE_URL", "value": "${{ secrets.HOMOLOG_BASE_URL }}"},
                {"name": "AUTH_MODE", "value": "login"},
                {"name": "LOGIN_URL", "value": "/auth/login"},
                {"name": "LOGIN_USER", "value": "${{ secrets.HOMOLOG_TEST_USER }}"},
                {"name": "LOGIN_PASS", "value": "${{ secrets.HOMOLOG_TEST_PASS }}"},
                {"name": "MAX_USERS", "value": "100"},
                {"name": "SPAWN_RATE", "value": "5"},
                {"name": "RUN_TIME", "value": "30m"},
                {"name": "HEADLESS", "value": "true"}
              ]
            }]
          }'
      env:
        AWS_DEFAULT_REGION: ${{ secrets.AWS_REGION }}
        AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
        AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}

    - name: Wait for Task Completion
      run: |
        # Monitor task execution and wait for completion
        python3 scripts/monitor_fargate_task.py \
          --cluster ${{ secrets.FARGATE_CLUSTER }} \
          --timeout 3600

    - name: Download Results from S3
      run: |
        # Download test results from S3 bucket
        aws s3 sync s3://${{ secrets.RESULTS_BUCKET }}/load-tests/ ./reports/

    - name: Generate Performance Report
      run: |
        # Generate comprehensive performance analysis
        python3 scripts/generate_performance_report.py \
          --input reports/ \
          --output performance-analysis.html \
          --compare-baseline

    - name: Upload Homologation Reports
      uses: actions/upload-artifact@v3
      with:
        name: homologation-test-reports
        path: |
          reports/
          performance-analysis.html
        retention-days: 90

  production-validation:
    name: Production Validation Tests
    runs-on: ubuntu-latest
    needs: load-test-homologation
    if: github.ref == 'refs/heads/main'
    environment: production

    steps:
    - name: Run Production Health Check
      run: |
        docker run --rm \
          -e OPENAPI_URL=${{ secrets.PROD_OPENAPI_URL }} \
          -e BASE_URL=${{ secrets.PROD_BASE_URL }} \
          -e AUTH_MODE=apikey \
          -e API_KEY=${{ secrets.PROD_API_KEY }} \
          -e MAX_USERS=5 \
          -e SPAWN_RATE=1 \
          -e RUN_TIME=5m \
          -e SPEC_INCLUDE_TAGS=health,public \
          -e HEADLESS=true \
          ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
```

## AWS Fargate Deployment

### Task Definition

Create an ECS Task Definition for load testing:

```json
{
  "family": "load-testing-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "2048",
  "memory": "4096",
  "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::ACCOUNT:role/loadTestingTaskRole",
  "containerDefinitions": [
    {
      "name": "load-tester",
      "image": "your-registry/dynamic-stress-tests:latest",
      "essential": true,
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/load-testing",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "environment": [
        {
          "name": "AWS_DEFAULT_REGION",
          "value": "us-east-1"
        }
      ],
      "secrets": [
        {
          "name": "OPENAPI_URL",
          "valueFrom": "arn:aws:ssm:us-east-1:ACCOUNT:parameter/load-testing/openapi-url"
        },
        {
          "name": "BASE_URL",
          "valueFrom": "arn:aws:ssm:us-east-1:ACCOUNT:parameter/load-testing/base-url"
        },
        {
          "name": "JWT_TOKEN",
          "valueFrom": "arn:aws:ssm:us-east-1:ACCOUNT:parameter/load-testing/jwt-token"
        }
      ],
      "mountPoints": [
        {
          "sourceVolume": "results-volume",
          "containerPath": "/app/reports"
        }
      ]
    },
    {
      "name": "results-uploader",
      "image": "amazon/aws-cli:latest",
      "essential": false,
      "dependsOn": [
        {
          "containerName": "load-tester",
          "condition": "SUCCESS"
        }
      ],
      "command": [
        "s3", "sync", "/app/reports/", "s3://your-results-bucket/load-tests/$(date +%Y%m%d-%H%M%S)/"
      ],
      "mountPoints": [
        {
          "sourceVolume": "results-volume",
          "containerPath": "/app/reports"
        }
      ]
    }
  ],
  "volumes": [
    {
      "name": "results-volume"
    }
  ]
}
```

### Fargate Cluster Setup

```bash
# Create ECS Cluster
aws ecs create-cluster \
  --cluster-name load-testing-cluster \
  --capacity-providers FARGATE \
  --default-capacity-provider-strategy capacityProvider=FARGATE,weight=1

# Create VPC and Security Groups
aws ec2 create-vpc --cidr-block 10.0.0.0/16 --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=load-testing-vpc}]'

# Create security group for load testing
aws ec2 create-security-group \
  --group-name load-testing-sg \
  --description "Security group for load testing tasks" \
  --vpc-id vpc-xxxxxxxxx

# Allow outbound internet access
aws ec2 authorize-security-group-egress \
  --group-id sg-xxxxxxxxx \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0
```

### IAM Roles and Policies

#### Task Execution Role

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "ssm:GetParameter",
        "ssm:GetParameters",
        "ssm:GetParametersByPath"
      ],
      "Resource": "*"
    }
  ]
}
```

#### Task Role

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::your-results-bucket",
        "arn:aws:s3:::your-results-bucket/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "cloudwatch:PutMetricData"
      ],
      "Resource": "*"
    }
  ]
}
```

## Homologation Environment Testing

### Environment Setup

The homologation environment should mirror production as closely as possible:

```yaml
# docker-compose.homolog.yml
version: '3.8'

services:
  load-tester:
    build: .
    environment:
      - OPENAPI_URL=${HOMOLOG_OPENAPI_URL}
      - BASE_URL=${HOMOLOG_BASE_URL}
      - AUTH_MODE=login
      - LOGIN_URL=/auth/login
      - LOGIN_USER=${HOMOLOG_TEST_USER}
      - LOGIN_PASS=${HOMOLOG_TEST_PASS}
      - MAX_USERS=100
      - SPAWN_RATE=5
      - RUN_TIME=30m
      - SPEC_INCLUDE_TAGS=public,core,premium
      - HEADLESS=true
      - RESULTS_BUCKET=${RESULTS_BUCKET}
    volumes:
      - ./reports:/app/reports
      - ~/.aws:/root/.aws:ro
    depends_on:
      - monitoring

  monitoring:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - ./monitoring/grafana:/etc/grafana/provisioning

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
```

### Testing Scenarios for Homologation

#### Comprehensive Load Testing

```bash
# Production-equivalent load test
docker run --rm \
  -e OPENAPI_URL=${HOMOLOG_OPENAPI_URL} \
  -e BASE_URL=${HOMOLOG_BASE_URL} \
  -e AUTH_MODE=login \
  -e LOGIN_URL=/auth/login \
  -e LOGIN_USER=${HOMOLOG_TEST_USER} \
  -e LOGIN_PASS=${HOMOLOG_TEST_PASS} \
  -e MAX_USERS=200 \
  -e SPAWN_RATE=10 \
  -e RUN_TIME=60m \
  -e SPEC_INCLUDE_TAGS=public,core,premium \
  -e HEADLESS=true \
  -v $(pwd)/reports:/app/reports \
  your-registry/dynamic-stress-tests:latest
```

#### Spike Testing

```bash
# Sudden traffic spike simulation
docker run --rm \
  -e OPENAPI_URL=${HOMOLOG_OPENAPI_URL} \
  -e BASE_URL=${HOMOLOG_BASE_URL} \
  -e AUTH_MODE=jwt \
  -e JWT_TOKEN=${HOMOLOG_JWT_TOKEN} \
  -e MAX_USERS=500 \
  -e SPAWN_RATE=50 \
  -e RUN_TIME=15m \
  -e SPEC_INCLUDE_TAGS=critical \
  -e HEADLESS=true \
  -v $(pwd)/reports:/app/reports \
  your-registry/dynamic-stress-tests:latest
```

#### Endurance Testing

```bash
# Extended duration testing
docker run --rm \
  -e OPENAPI_URL=${HOMOLOG_OPENAPI_URL} \
  -e BASE_URL=${HOMOLOG_BASE_URL} \
  -e AUTH_MODE=apikey \
  -e API_KEY=${HOMOLOG_API_KEY} \
  -e MAX_USERS=100 \
  -e SPAWN_RATE=2 \
  -e RUN_TIME=4h \
  -e SPEC_INCLUDE_TAGS=stable \
  -e HEADLESS=true \
  -v $(pwd)/reports:/app/reports \
  your-registry/dynamic-stress-tests:latest
```

## Jenkins Pipeline Integration

```groovy
pipeline {
    agent any

    environment {
        REGISTRY_URL = 'your-registry.com'
        IMAGE_NAME = 'dynamic-stress-tests'
        HOMOLOG_CLUSTER = 'homolog-cluster'
        PROD_CLUSTER = 'prod-cluster'
    }

    stages {
        stage('Build') {
            steps {
                script {
                    docker.build("${REGISTRY_URL}/${IMAGE_NAME}:${BUILD_NUMBER}")
                }
            }
        }

        stage('Staging Tests') {
            when {
                branch 'develop'
            }
            steps {
                script {
                    docker.image("${REGISTRY_URL}/${IMAGE_NAME}:${BUILD_NUMBER}").inside() {
                        sh '''
                            export OPENAPI_URL=${STAGING_OPENAPI_URL}
                            export BASE_URL=${STAGING_BASE_URL}
                            export AUTH_MODE=jwt
                            export JWT_TOKEN=${STAGING_JWT_TOKEN}
                            export MAX_USERS=25
                            export SPAWN_RATE=3
                            export RUN_TIME=10m
                            export HEADLESS=true
                            make demo
                        '''
                    }
                }
                archiveArtifacts artifacts: 'reports/**/*', fingerprint: true
            }
        }

        stage('Homologation Tests') {
            when {
                branch 'main'
            }
            steps {
                script {
                    // Deploy to Fargate for homologation testing
                    sh '''
                        aws ecs run-task \
                            --cluster ${HOMOLOG_CLUSTER} \
                            --task-definition load-testing-homolog \
                            --launch-type FARGATE \
                            --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}"
                    '''

                    // Wait for completion and download results
                    sh '''
                        python3 scripts/wait_for_fargate_completion.py --cluster ${HOMOLOG_CLUSTER}
                        aws s3 sync s3://homolog-results-bucket/ ./reports/
                    '''
                }

                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'reports',
                    reportFiles: 'report.html',
                    reportName: 'Homologation Load Test Report'
                ])
            }
        }

        stage('Production Validation') {
            when {
                branch 'main'
            }
            input {
                message "Deploy to production?"
                ok "Deploy"
                parameters {
                    choice(name: 'VALIDATION_LEVEL', choices: ['health', 'basic', 'full'], description: 'Validation level for production')
                }
            }
            steps {
                script {
                    def maxUsers = params.VALIDATION_LEVEL == 'health' ? 1 : (params.VALIDATION_LEVEL == 'basic' ? 5 : 10)

                    docker.image("${REGISTRY_URL}/${IMAGE_NAME}:${BUILD_NUMBER}").inside() {
                        sh """
                            export OPENAPI_URL=${PROD_OPENAPI_URL}
                            export BASE_URL=${PROD_BASE_URL}
                            export AUTH_MODE=apikey
                            export API_KEY=${PROD_API_KEY}
                            export MAX_USERS=${maxUsers}
                            export SPAWN_RATE=1
                            export RUN_TIME=5m
                            export SPEC_INCLUDE_TAGS=health,public
                            export HEADLESS=true
                            make demo
                        """
                    }
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/**/*', allowEmptyArchive: true
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'reports',
                reportFiles: 'report.html',
                reportName: 'Load Test Report'
            ])
        }
        success {
            slackSend(
                channel: '#deployment',
                color: 'good',
                message: "Load testing completed successfully for ${env.JOB_NAME} - ${env.BUILD_NUMBER}"
            )
        }
        failure {
            slackSend(
                channel: '#deployment',
                color: 'danger',
                message: "Load testing failed for ${env.JOB_NAME} - ${env.BUILD_NUMBER}"
            )
        }
    }
}
```

## Performance Gates and Quality Thresholds

### Performance Gate Script

```python
#!/usr/bin/env python3
# scripts/performance_gate.py

import json
import sys
import argparse
from pathlib import Path

def check_performance_thresholds(report_path, thresholds):
    """Check if performance metrics meet quality gates"""

    with open(report_path) as f:
        report_data = json.load(f)

    failures = []

    # Check average response time
    avg_response_time = report_data.get('average_response_time', 0)
    if avg_response_time > thresholds['max_avg_response_time']:
        failures.append(f"Average response time ({avg_response_time}ms) exceeds threshold ({thresholds['max_avg_response_time']}ms)")

    # Check error rate
    error_rate = report_data.get('error_rate', 0)
    if error_rate > thresholds['max_error_rate']:
        failures.append(f"Error rate ({error_rate}%) exceeds threshold ({thresholds['max_error_rate']}%)")

    # Check requests per second
    rps = report_data.get('requests_per_second', 0)
    if rps < thresholds['min_rps']:
        failures.append(f"RPS ({rps}) below minimum threshold ({thresholds['min_rps']})")

    return failures

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Performance quality gate checker')
    parser.add_argument('--report', required=True, help='Path to performance report')
    parser.add_argument('--max-avg-response-time', type=int, default=1000, help='Maximum average response time (ms)')
    parser.add_argument('--max-error-rate', type=float, default=5.0, help='Maximum error rate (%)')
    parser.add_argument('--min-rps', type=float, default=1.0, help='Minimum requests per second')

    args = parser.parse_args()

    thresholds = {
        'max_avg_response_time': args.max_avg_response_time,
        'max_error_rate': args.max_error_rate,
        'min_rps': args.min_rps
    }

    failures = check_performance_thresholds(args.report, thresholds)

    if failures:
        print("💀 Performance quality gate FAILED:")
        for failure in failures:
            print(f"  - {failure}")
        sys.exit(1)
    else:
        print("✅ Performance quality gate PASSED")
        sys.exit(0)
```

## Monitoring and Alerting

### CloudWatch Integration

```yaml
# cloudwatch-monitoring.yml
version: '3.8'

services:
  load-tester:
    build: .
    environment:
      - AWS_DEFAULT_REGION=us-east-1
      - CLOUDWATCH_NAMESPACE=LoadTesting
    volumes:
      - ./reports:/app/reports
    command: >
      sh -c "
        make demo &&
        python3 scripts/publish_metrics.py --namespace LoadTesting --reports ./reports/
      "
```

### Metrics Publishing Script

```python
#!/usr/bin/env python3
# scripts/publish_metrics.py

import boto3
import json
import argparse
from datetime import datetime

def publish_load_test_metrics(namespace, report_path):
    """Publish load test metrics to CloudWatch"""

    cloudwatch = boto3.client('cloudwatch')

    with open(report_path) as f:
        report_data = json.load(f)

    metrics = [
        {
            'MetricName': 'AverageResponseTime',
            'Value': report_data.get('average_response_time', 0),
            'Unit': 'Milliseconds'
        },
        {
            'MetricName': 'ErrorRate',
            'Value': report_data.get('error_rate', 0),
            'Unit': 'Percent'
        },
        {
            'MetricName': 'RequestsPerSecond',
            'Value': report_data.get('requests_per_second', 0),
            'Unit': 'Count/Second'
        }
    ]

    for metric in metrics:
        cloudwatch.put_metric_data(
            Namespace=namespace,
            MetricData=[{
                'MetricName': metric['MetricName'],
                'Value': metric['Value'],
                'Unit': metric['Unit'],
                'Timestamp': datetime.utcnow()
            }]
        )

    print(f"Published {len(metrics)} metrics to CloudWatch namespace: {namespace}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Publish load test metrics to CloudWatch')
    parser.add_argument('--namespace', required=True, help='CloudWatch namespace')
    parser.add_argument('--reports', required=True, help='Path to reports directory')

    args = parser.parse_args()

    report_file = f"{args.reports}/results.json"
    publish_load_test_metrics(args.namespace, report_file)
```

This comprehensive CI/CD integration guide ensures that load testing becomes an integral part of your deployment pipeline, providing automated performance validation at every stage from development to production.