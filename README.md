DevOps Error Monitoring with CloudWatch & SNS
Project Overview

This project demonstrates a real-time log monitoring and alerting system using AWS CloudWatch and SNS.
The system monitors logs from an EC2 instance (application logs) and triggers email alerts whenever errors are detected.

Key Features:

Real-time log monitoring using CloudWatch Agent

Automatic extraction of metrics from log patterns using Metric Filters

Threshold-based CloudWatch Alarms for critical errors

Instant notifications via SNS email subscription

Easily extensible for Slack, Lambda, SMS, or other endpoints

This setup helps prevent downtime and speeds up incident response in production environments.

Architecture
EC2 Instance (app generating logs)
         │
         ▼
CloudWatch Agent (installed on EC2)
         │
         ▼
CloudWatch Logs (stores raw logs)
         │
         ▼
Metric Filter (extracts ERROR count)
         │
         ▼
CloudWatch Alarm (monitors metric threshold)
         │
         ▼
SNS Topic (sends notifications)
         │
         ▼
Email / SMS / Slack / Lambda

Explanation of Flow:

CloudWatch Agent runs on EC2 and monitors /var/log/app.log.

Logs are pushed to CloudWatch Logs.

A Metric Filter scans logs for the keyword "ERROR" and converts each match into a numeric metric called ErrorCount.

CloudWatch Alarm monitors ErrorCount and triggers when the threshold is breached (e.g., > 1 error per minute).

Alarm action publishes to an SNS topic, sending instant alerts to subscribed endpoints (email, Slack, etc.).

Setup Instructions
1. Install CloudWatch Agent on EC2
# Update packages
sudo apt update && sudo apt install -y unzip

# Download CloudWatch Agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb

# Install
sudo dpkg -i amazon-cloudwatch-agent.deb
2. Configure CloudWatch Agent

Create /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json with:

{
    "agent": {
        "run_as_user": "root"
    },
    "logs": {
        "logs_collected": {
            "files": {
                "collect_list": [
                    {
                        "file_path": "/var/log/app.log",
                        "log_group_name": "devops-ai-log-monitor",
                        "log_stream_name": "{instance_id}",
                        "retention_in_days": 30
                    }
                ]
            }
        }
    }
}

Start the agent:

sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config -m ec2 -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json -s
3. IAM Role for EC2

Attach the following AWS managed policies to your EC2 instance role:

AmazonSSMManagedInstanceCore (optional, for SSM)

CloudWatchAgentServerPolicy (required for logs/metrics)

4. Create Metric Filter
aws logs put-metric-filter \
    --log-group-name devops-ai-log-monitor \
    --filter-name "ErrorCountFilter" \
    --filter-pattern "ERROR" \
    --metric-transformations \
        metricName=ErrorCount,metricNamespace=DevOpsMonitoring,metricValue=1 \
    --region ap-south-1

Test the filter:

aws logs test-metric-filter \
    --log-group-name devops-ai-log-monitor \
    --filter-pattern "ERROR" \
    --log-event-messages '["ERROR: DevOps monitoring test"]' \
    --region ap-south-1
5. Create CloudWatch Alarm
aws cloudwatch put-metric-alarm \
    --alarm-name DevOpsErrorAlert \
    --alarm-description "Error Alert" \
    --metric-name ErrorCount \
    --namespace DevOpsMonitoring \
    --statistic Sum \
    --period 60 \
    --evaluation-periods 1 \
    --threshold 1 \
    --comparison-operator GreaterThanThreshold \
    --alarm-actions arn:aws:sns:ap-south-1:ACCOUNT_ID:Default_CloudWatch_Alarms_Topic \
    --region ap-south-1
6. Setup SNS Topic
# Create Topic
aws sns create-topic --name Default_CloudWatch_Alarms_Topic --region ap-south-1

# Subscribe email
aws sns subscribe \
    --topic-arn arn:aws:sns:ap-south-1:ACCOUNT_ID:Default_CloudWatch_Alarms_Topic \
    --protocol email \
    --notification-endpoint "your-email@example.com" \
    --region ap-south-1

The subscriber will receive a confirmation email. Must confirm to receive alerts.

Test SNS notification:

aws sns publish \
    --topic-arn arn:aws:sns:ap-south-1:ACCOUNT_ID:Default_CloudWatch_Alarms_Topic \
    --subject "Test Alert" \
    --message "This is a test alert from DevOpsErrorAlert" \
    --region ap-south-1
7. Generate Logs to Test
echo "ERROR: DevOps monitoring test" >> /var/log/app.log

Wait for CloudWatch metric update (approx. 1 min)

Check alarm state → IN ALARM

Email alert should arrive immediately.

8. Verify Metric
aws cloudwatch get-metric-statistics \
    --metric-name ErrorCount \
    --namespace DevOpsMonitoring \
    --start-time $(date -u -d '5 minutes ago' +"%Y-%m-%dT%H:%M:%SZ") \
    --end-time $(date -u +"%Y-%m-%dT%H:%M:%SZ") \
    --period 60 \
    --statistics Sum \
    --region ap-south-1
UI / Monitoring

CloudWatch Console → Logs: view all log streams.

CloudWatch Console → Metrics: see ErrorCount metric updating in real-time.

CloudWatch Console → Alarms: monitor alarm state (OK / IN ALARM).

SNS Console → Topics: verify subscription status and sent messages.

Troubleshooting Tips

Alarm not triggering: verify metric filter, log group, log stream, period, and threshold.

No email alert: check SNS subscription confirmation.

Duplicate metrics: delete old metric filters to avoid conflicts.

High-frequency logs: increase metric period or use sum over multiple periods.

