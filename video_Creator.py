import json
import base64
import json
import io
import os
import time
from datetime import datetime
from pathlib import Path
from threading import Thread

import boto3
import cv2
from PIL import Image

AWS_S3_CREDS = {
    "aws_access_key_id":"************",
    "aws_secret_access_key":"*************"
}

sqs = boto3.client("sqs", region_name='us-east-1',**AWS_S3_CREDS)
request_queue = 'https://sqs.us-east-1.amazonaws.com/*************'
response_queue = 'https://sqs.us-east-1.amazonaws.com/***************'
video_queue = 'https://sqs.us-east-1.amazonaws.com/*******************'
s3 = boto3.client('s3', region_name='us-east-1', **AWS_S3_CREDS)


def base64_to_image(image_name, data):
    base64_data = data.encode('utf-8')
    with open('/tmp/images/'+image_name, "wb") as fh:
        fh.write(base64.decodebytes(base64_data))

def put_file_s3(bucket_name, key, file_path):
    try:
        s3.upload_file(file_path, Bucket=bucket_name,Key=key)
        return True
    except Exception as e:
        print(e)
        return False

def stitch_images():
    image_folder = '/tmp/images'
    video_name = '/tmp/video.avi'

    images = [img for img in os.listdir(image_folder) if img.endswith(".jpeg")]
    images.sort()
    print(f"Number of images: {len(images)}")
    print(images)
    frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, layers = frame.shape
    fps = 10
    video = cv2.VideoWriter(video_name, 0, fps, (width,height))

    for image in images:
        video.write(cv2.imread(os.path.join(image_folder, image)))
    
    cv2.destroyAllWindows()
    video.release()

def receive_message():
    messages = []
    response = sqs.receive_message(
        QueueUrl=video_queue,
        MaxNumberOfMessages=10,
    )
    for message in response.get("Messages", []):
        messages.append(message)
    return messages

def lambda_handler(event, context):
    max_recheck = 1000
    i = 0
    if not os.path.exists('/tmp/images/'):
        print("Creating '/tmp/images/' directory")
        os.system('mkdir /tmp/images')
    messages = list(receive_message())
    while len(messages) > 0:
        for message in messages:
            message_body = message["Body"]
            loaded_message = json.loads(message_body)
            image_name = loaded_message['image_name']
            image_data = loaded_message['image_data']
            base64_to_image(image_name, image_data)
        messages = list(receive_message())
        i += 1
        
    print(f"No more messages found in the Queue. Received {i} images")
    
    print("Stitching Images")
    s3_video_bucket = 'face-recognition-result-data'
    stitch_images()
    put_file_s3(bucket_name=s3_video_bucket, key='video.avi', file_path='/tmp/video.avi')
    os.remove('/tmp/video.avi')
    print(f"Final video has been written to S3 bucket '{s3_video_bucket}'")
    print(f"Purging videoQueue")
    response = sqs.purge_queue(
        QueueUrl=video_queue
    )
    print(f"Purge Response: {response}")
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps(f"Video has been successfully written to S3 bucket: '{s3_video_bucket}'")
    }
