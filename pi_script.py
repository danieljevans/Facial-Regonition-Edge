import base64
import json
import io
import os
import os.path
import time
from datetime import datetime
from pathlib import Path
from threading import Thread
import datetime
import requests


import boto3
import cv2
from PIL import Image

try:
    import picamera
    from picamera.array import PiRGBArray
except:
    print('Testing locally')


AWS_S3_CREDS = {
    "aws_access_key_id":"*************",
    "aws_secret_access_key":"***********"
}

sqs = boto3.client("sqs", region_name='us-east-1',**AWS_S3_CREDS)
request_queue = 'https://sqs.us-east-1.amazonaws.com/*************'
response_queue = 'https://sqs.us-east-1.amazonaws.com/**************'
video_queue = 'https://sqs.us-east-1.amazonaws.com/**************'

video_stitch_lambda = boto3.client('lambda', region_name='us-east-1',**AWS_S3_CREDS)

def main(record_time):
    os.system('rm -rf image*')
    os.system('rm -rf time_*')
    Thread(target=get_recognition_result, daemon=True).start()
    Thread(target=print_results, daemon=True).start()
    facial_recognition(record_time)

def print_results():
    i = 5
    while True:
        filename = f'image{str(i).zfill(4)}.jpeg.txt'
        if os.path.isfile(filename):
            with open(filename, 'r') as file:
                person_num = int(i/5)
                print(f"The {person_num} recognized " + str(file.read()))
            os.system(f'rm -rf {filename}')
            
            if os.path.isfile(f'time_{filename}'):
                with open(f'time_{filename}', 'r') as file:
                    # Script takes approximately half a second to write/read local file (not counted for Lambda)
                    file_read_adjusted_dt = datetime.datetime.now() - datetime.timedelta(seconds=0.5)
                    dt = datetime.datetime.strptime(file.read(), '%Y-%m-%d %H:%M:%S.%f')
                    latency = file_read_adjusted_dt - dt
                    print("Latency: " + str(latency.total_seconds()) + ' seconds')
                os.system(f'rm -rf time_{filename}')
            
            i += 5
        else:
            time.sleep(1)

def facial_recognition(record_time):
    reduction_factor = 0.035
    end_t = time.time() + record_time
    with picamera.PiCamera() as camera:
        camera.resolution = (160, 160)
        camera.framerate = 30
        rawCapture = PiRGBArray(camera, size=(160, 160))

        i = 1
        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
            image = frame.array
            rawCapture.truncate(0)
            filename = f'image{str(i).zfill(4)}.jpeg'
            cv2.imwrite(filename, image)
            Thread(target=compress_and_queue_for_video_storage, args=(filename,)).start()
            if i % 5 == 0:
                Thread(target=compress_and_queue_for_recognition, args=(filename,)).start()
                pass
            i += 1
            time.sleep(reduction_factor)
            if time.time() > end_t or i >= 3000:
                break
    time.sleep(1)
    url = 'https://************.execute-api.us-east-1.amazonaws.com/*******/videoProcessorLayerTest'
    response = requests.post(url)
    time.sleep(1)
    print('\nScript Finished')
    os.sys.exit()

def compress_and_queue_for_recognition(filename):
    image_data = image_to_base64(filename)
    queue_file(filename, image_data)

def compress_and_queue_for_video_storage(filename):
    image_data = image_to_base64(filename)
    queue_file_video(filename, image_data)

def compress_image(filename):
    with Image.open(filename) as im1:
        im2 = im1.resize((160, 160))
        im2.save(filename)

#************ SQS ************
def image_to_base64(image_name):
    with open(image_name, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    encoded_string = encoded_string.decode('utf-8')
    return encoded_string

def base64_to_image(image_name, data):
    base64_data = data.encode('utf-8')
    with open(image_name, "wb") as fh:
        fh.write(base64.decodebytes(base64_data))

def queue_file(file_name, file_data):
    message = {'image_name': file_name,
            'image_data': file_data,}
    sqs.send_message(
        QueueUrl=request_queue,
        MessageBody=(json.dumps(message))
    )
    with open(f'time_{file_name}.txt', 'w') as file:
        file.write(str(datetime.datetime.now()))
    os.system(f'rm -rf {file_name}')

def queue_file_video(file_name, file_data):
    message = {'image_name': file_name,
            'image_data': file_data}
    sqs.send_message(
        QueueUrl=video_queue,
        MessageBody=(json.dumps(message))
    )
    os.system(f'rm -rf {file_name}')

def delete_message(receipt_handle):
    sqs.delete_message(
        QueueUrl=response_queue,
        ReceiptHandle=receipt_handle,
    )

def receive_message():
    messages = []
    response = sqs.receive_message(
        QueueUrl=response_queue,
        MaxNumberOfMessages=10,
    )
    for message in response.get("Messages", []):
        messages.append(message)
    return messages

def get_recognition_result():
    try:
        print("Wating for first result...")
        while True:
            messages = receive_message()
            for message in messages:
                message_body = message["Body"]
                struct = json.loads(message_body)
                file_name = str(struct['file_name']) + '.txt'
                with open (file_name, 'w') as file:
                    file.write(message_body)
                delete_message(message['ReceiptHandle'])
            
    
    except Exception as e:
        print(e)

if __name__ == "__main__":
    record_time = 300
    main(record_time)
    