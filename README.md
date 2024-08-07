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


Please refer to the [Amazon OpenSearch Service Guide](./Amazon%20OpenSearch%20Service%20_%20us-west-1.pdf) for detailed information.

1. Since We're using a pre-existing domain `ts-cybersec--is-2024-os-aa` we can move on to the next step.

### Create/Configure Lambda Function

There is a pre-existing function already called `S3ToFluentBitTrigger` but if you need to make a new function this is how you would do it:

1. Go to AWS Lambda Console:
    - Navigate to the AWS Management Console.
    - Choose the Lambda service.
2. Create a New Lambda Function:
    - Click on Create function.
    - Select Author from scratch.
    - Enter a function name (e.g., S3ToFluentBitTrigger).
    - Choose Python 3.12 as the runtime.
    - Under Permissions, choose Create a new role with basic Lambda permissions.
    - Click Create function.
3. Prepare Lambda Function Code:
    - `lambda_function.py`
4. Set Up Execution Role:
    - Go to the IAM console.
    - Create a new policy with permissions for S3 and OpenSearch.
    - Attach the policy to the Lambda execution role.
5. Add an S3 Trigger:
    - Go back to the Lambda console.
    - Select your Lambda function.
    - Click Add trigger.
    - Select S3.
    - Choose your bucket.
    - Set the event type to ObjectCreated.
    - Add a suffix (e.g., .log).
    - Click Add.
6. Set up Enviroment Variables:

BUCKET_NAME       | “s3 bucket name”

EC2_INSTANCE_ID   |“ec2 instance id”

REMOTE_PATH       |“destination path where your logs are stored in ec2”

### EC2 Instance Setup
1. Launch an EC2 instance from the AWS Management Console.
2. Configure security groups to allow necessary traffic (e.g., SSH, HTTP, HTTPS).
3. Connect to the EC2 instance using SSH.
4. Create a folder called `logs`

### Fluent Bit Installation
1. Install Fluent Bit on the EC2 instance.
2. Configure Fluent Bit using `fluent-bit.conf` and `parsers.conf` files.

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
```
#### Example `parsers.conf`
```ini
[PARSER]
    Name   apache
    Format regex
    Regex  ^(?<host>[^ ]*) [^ ]* (?<user>[^ ]*) \[(?<time>[^\]]*)\] "(?<method>\S+)(?: +(?<path>[^\"]*?)(?: +\S*)?)?" (?<code>[^ ]*) (?<size>[^ ]*)(?: "(?<referer>[^\"]*)" "(?<agent>[^\"]*)")?$
    Time_Key time
    Time_Format %d/%b/%Y:%H:%M:%S %z

[PARSER]
    Name   apache2
    Format regex
    Regex  ^(?<host>[^ ]*) [^ ]* (?<user>[^ ]*) \[(?<time>[^\]]*)\] "(?<method>\S+)(?: +(?<path>[^ ]*) +\S*)?" (?<code>[^ ]*) (?<size>[^ ]*)(?: "(?<referer>[^\"]*)" "(?<agent>.*)")?$
    Time_Key time
    Time_Format %d/%b/%Y:%H:%M:%S %z

[PARSER]
    Name   apache_error
    Format regex
    Regex  ^\[[^ ]* (?<time>[^\]]*)\] \[(?<level>[^\]]*)\](?: \[pid (?<pid>[^\]]*)\])?( \[client (?<client>[^\]]*)\])? (?<message>.*)$

[PARSER]
    Name   nginx
    Format regex
    Regex ^(?<remote>[^ ]*) (?<host>[^ ]*) (?<user>[^ ]*) \[(?<time>[^\]]*)\] "(?<method>\S+)(?: +(?<path>[^\"]*?)(?: +\S*)?)?" (?<code>[^ ]*) (?<size>[^ ]*)(?: "(?<referer>[^\"]*)" "(?<agent>[^\"]*)")
    Time_Key time
    Time_Format %d/%b/%Y:%H:%M:%S %z

[PARSER]
    Name        k8s-nginx-ingress
    Format      regex
    Regex       ^(?<host>[^ ]*) - (?<user>[^ ]*) \[(?<time>[^\]]*)\] "(?<method>\S+)(?: +(?<path>[^\"]*?)(?: +\S*)?)?" (?<code>[^ ]*) (?<size>[^ ]*) "(?<referer>[^\"]*)" "(?<agent>[^\"]*)" (?<request_length>[^ ]*) (?<request_time>[^ ]*) \[(?<proxy_upstream_name>[^ ]*)\] (\[(?<proxy_alternative_upstream_name>[^ ]*)\] )?(?<upstream_addr>[^ ]*) (?<upstream_response_length>[^ ]*) (?<upstream_response_time>[^ ]*) (?<upstream_status>[^ ]*) (?<reg_id>[^ ]*).*$
    Time_Key    time
    Time_Format %d/%b/%Y:%H:%M:%S %z

[PARSER]
    Name   json
    Format json
    Time_Key time
    Time_Format %d/%b/%Y:%H:%M:%S %z

[PARSER]
    Name   logfmt
    Format logfmt

[PARSER]
    Name         docker
    Format       json
    Time_Key     time
    Time_Format  %Y-%m-%dT%H:%M:%S.%L
    Time_Keep    On

[PARSER]
    Name        docker-daemon
    Format      regex
    Regex       time="(?<time>[^ ]*)" level=(?<level>[^ ]*) msg="(?<msg>[^ ].*)"
    Time_Key    time
    Time_Format %Y-%m-%dT%H:%M:%S.%L
    Time_Keep   On

[PARSER]
    Name        syslog-rfc5424
    Format      regex
    Regex       ^\<(?<pri>[0-9]{1,5})\>1 (?<time>[^ ]+) (?<host>[^ ]+) (?<ident>[^ ]+) (?<pid>[-0-9]+) (?<msgid>[^ ]+) (?<extradata>(\[(.*?)\]|-)) (?<message>.+)$
    Time_Key    time
    Time_Format %Y-%m-%dT%H:%M:%S.%L%z
    Time_Keep   On

[PARSER]
    Name        syslog-rfc3164-local
    Format      regex
    Regex       ^\<(?<pri>[0-9]+)\>(?<time>[^ ]* {1,2}[^ ]* [^ ]*) (?<ident>[a-zA-Z0-9_\/\.\-]*)(?:\[(?<pid>[0-9]+)\])?(?:[^\:]*\:)? *(?<message>.*)$
    Time_Key    time
    Time_Format %b %d %H:%M:%S
    Time_Keep   On

[PARSER]
    Name        syslog-rfc3164
    Format      regex
    Regex       /^\<(?<pri>[0-9]+)\>(?<time>[^ ]* {1,2}[^ ]* [^ ]*) (?<host>[^ ]*) (?<ident>[a-zA-Z0-9_\/\.\-]*)(?:\[(?<pid>[0-9]+)\])?(?:[^\:]*\:)? *(?<message>.*)$/
    Time_Key    time
    Time_Format %b %d %H:%M:%S
    Time_Keep   On

[PARSER]
    Name    mongodb
    Format  regex
    Regex   ^(?<time>[^ ]*)\s+(?<severity>\w)\s+(?<component>[^ ]+)\s+\[(?<context>[^\]]+)]\s+(?<message>.*?) *(?<ms>(\d+))?(:?ms)?$
    Time_Format %Y-%m-%dT%H:%M:%S.%L
    Time_Keep   On
    Time_Key time

[PARSER]
    Name    envoy
    Format  regex
    Regex ^\[(?<start_time>[^\]]*)\] "(?<method>\S+)(?: +(?<path>[^\"]*?)(?: +\S*)?)? (?<protocol>\S+)" (?<code>[^ ]*) (?<response_flags>[^ ]*) (?<bytes_received>[^ ]*) (?<bytes_sent>[^ ]*) (?<duration>[^ ]*) (?<x_envoy_upstream_service_time>[^ ]*) "(?<x_forwarded_for>[^ ]*)" "(?<user_agent>[^\"]*)" "(?<request_id>[^\"]*)" "(?<authority>[^ ]*)" "(?<upstream_host>[^ ]*)"
    Time_Format %Y-%m-%dT%H:%M:%S.%L%z
    Time_Keep   On
    Time_Key start_time

[PARSER]
    Name    istio-envoy-proxy
    Format  regex
    Regex ^\[(?<start_time>[^\]]*)\] "(?<method>\S+)(?: +(?<path>[^\"]*?)(?: +\S*)?)? (?<protocol>\S+)" (?<response_code>[^ ]*) (?<response_flags>[^ ]*) (?<response_code_details>[^ ]*) (?<connection_termination_details>[^ ]*) (?<upstream_transport_failure_reason>[^ ]*) (?<bytes_received>[^ ]*) (?<bytes_sent>[^ ]*) (?<duration>[^ ]*) (?<x_envoy_upstream_service_time>[^ ]*) "(?<x_forwarded_for>[^ ]*)" "(?<user_agent>[^\"]*)" "(?<x_request_id>[^\"]*)" (?<authority>[^ ]*)" "(?<upstream_host>[^ ]*)" (?<upstream_cluster>[^ ]*) (?<upstream_local_address>[^ ]*) (?<downstream_local_address>[^ ]*) (?<downstream_remote_address>[^ ]*) (?<requested_server_name>[^ ]*) (?<route_name>[^  ]*)
    Time_Format %Y-%m-%dT%H:%M:%S.%L%z
    Time_Keep   On
    Time_Key start_time

[PARSER]
    Name cri
    Format regex
    Regex ^(?<time>[^ ]+) (?<stream>stdout|stderr) (?<logtag>[^ ]*) (?<message>.*)$
    Time_Key    time
    Time_Format %Y-%m-%dT%H:%M:%S.%L%z
    Time_Keep   On

[PARSER]
    Name    kube-custom
    Format  regex
    Regex   (?<tag>[^.]+)?\.?(?<pod_name>[a-z0-9](?:[-a-z0-9]*[a-z0-9])?(?:\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*)_(?<namespace_name>[^_]+)_(?<container_name>.+)-(?<docker_id>[a-z0-9]{64})\.log$

[PARSER]
    Name    kmsg-netfilter-log
    Format  regex
    Regex   ^\<(?<pri>[0-9]{1,5})\>1 (?<time>[^ ]+) (?<host>[^ ]+) kernel - - - \[[0-9\.]*\] (?<logprefix>[^ ]*)\s?IN=(?<in>[^ ]*) OUT=(?<out>[^ ]*) MAC=(?<macsrc>[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}):(?<macdst>[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}):(?<ethtype>[0-9a-f]{2}:[0-9a-f]{2}) SRC=(?<saddr>[^ ]*) DST=(?<daddr>[^ ]*) LEN=(?<len>[^ ]*) TOS=(?<tos>[^ ]*) PREC=(?<prec>[^ ]*) TTL=(?<ttl>[^ ]*) ID=(?<id>[^ ]*) (D*F*)\s*PROTO=(?<proto>[^ ]*)\s?((SPT=)?(?<sport>[0-9]*))\s?((DPT=)?(?<dport>[0-9]*))\s?((LEN=)?(?<protolen>[0-9]*))\s?((WINDOW=)?(?<window>[0-9]*))\s?((RES=)?(?<res>0?x?[0-9]*))\s?(?<flag>[^ ]*)\s?((URGP=)?(?<urgp>[0-9]*))
    Time_Key  time
    Time_Format  %Y-%m-%dT%H:%M:%S.%L%z
