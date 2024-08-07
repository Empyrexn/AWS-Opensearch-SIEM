import boto3
import os

s3_client = boto3.client('s3')
ssm_client = boto3.client('ssm')

EC2_INSTANCE_ID = os.environ['EC2_INSTANCE_ID']
REMOTE_PATH = os.environ['REMOTE_PATH']
BUCKET_NAME = os.environ['BUCKET_NAME']

def lambda_handler(event, context):
    object_key = event['Records'][0]['s3']['object']['key']

    # Create a command to download the file directly from S3 on the EC2 instance
    command = f"aws s3 cp s3://{BUCKET_NAME}/{object_key} {os.path.join(REMOTE_PATH, os.path.basename(object_key))}"
    
    try:
        response = ssm_client.send_command(
            InstanceIds=[EC2_INSTANCE_ID],
            DocumentName="AWS-RunShellScript",
            Parameters={'commands': [command]}
        )
        command_id = response['Command']['CommandId']
        waiter = ssm_client.get_waiter('command_executed')
        waiter.wait(CommandId=command_id, InstanceId=EC2_INSTANCE_ID)
    except boto3.exceptions.Boto3Error as e:
        print(f"An error occurred: {e}")

    return {
        'statusCode': 200,
        'body': f'Successfully transferred {object_key} to EC2 instance {EC2_INSTANCE_ID}'
    }
