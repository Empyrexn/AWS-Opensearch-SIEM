# AWS Opensearch SIEM Project Documentation

## Introduction

### Overview
The purpose of this project is to set up a Security Information and Event Management (SIEM) system using OpenSearch and Fluent Bit to monitor and alert on security events. The system is designed to detect and alert on specific security events, such as invalid SSH login attempts, Apache worker errors, and potential break-in attempts.

![image](https://github.com/user-attachments/assets/158381d8-ccaf-4a90-ae98-3f57c269eee3)


### Components
- Amazon S3
- AWS Lambda
- AWS SSM
- OpenSearch
- Fluent Bit
- AWS EC2
- Slack for notifications

## Prerequisites

### Software and Tools
- AWS EC2 instance
- AWS Lambda Function
- OpenSearch
- Fluent Bit
- Slack account
- Amazon S3 Bucket

### Code for Lambda Function
- `lambda_function.py`

### Configuration Files for Fluent Bit
- `fluent-bit.conf`
- `parsers.conf`

## Setup and Installation

### Create/Configure Amazon S3 Bucket
1. Since We're using a pre-existing bucket `ts-cybersec--is-2024-os-1` we can move on to the next step.

### Create/Configure Opensearch Domain
1. Since We're using a pre-existing domain `ts-cybersec--is-2024-os-aa` we can move on to the next step.

### Create/Configure Lambda Function
1. Go to AWS Lambda Console:
    - Navigate to the AWS Management Console.
    - Choose the Lambda service.
2. Create a New Lambda Function:
    - Click on Create function.
    - Select Author from scratch.
    - Enter a function name (e.g., S3ToOpenSearchFunction).
    - Choose Python 3.12 as the runtime.
    - Under Permissions, choose Create a new role with basic Lambda permissions.
    - Click Create function.
3. Prepare Lambda Function Code:



### EC2 Instance Setup
1. Launch an EC2 instance from the AWS Management Console.
2. Configure security groups to allow necessary traffic (e.g., SSH, HTTP, HTTPS).
3. Connect to the EC2 instance using SSH.
4. Create a folder called `logs`

### Fluent Bit Installation
1. Install Fluent Bit on the EC2 instance.
2. Configure Fluent Bit using `fluent-bit.conf` and `parsers.conf` files.

### OpenSearch Setup
1. Install OpenSearch on the EC2 instance.
2. Configure OpenSearch for the SIEM use case.
3. Create indices for storing logs.

### Configuration Files

#### Example `fluent-bit.conf`
```ini
[SERVICE]
    Parsers_File parsers.conf
    Flush        1
    Log_Level    info
    Daemon       off

[INPUT]
    Name        tail
    Path        /home/ec2-user/logs/*.log
    Parser      apache_ssh_parser
    Tag         apache_ssh_logs
    Refresh_Interval 5
    Read_From_Head true

[FILTER]
    Name          parser
    Match         apache_ssh_logs
    Key_Name      log
    Parser        apache_ssh_parser
    Reserve_Data  true

[FILTER]
    Name          parser
    Match         apache_ssh_logs
    Key_Name      log
    Parser        syslog_parser
    Reserve_Data  true

[OUTPUT]
    Name        opensearch
    Match       apache_ssh_logs
    Host        your-opensearch-domain
    Port        443
    Index       apache-ssh-logs-index-v6
    Type        _doc
    AWS_Auth    On
    AWS_Region  your-region
    tls         On
