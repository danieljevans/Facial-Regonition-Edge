import json, base64
import os
import boto3
import torch
import torchvision.transforms as transforms
from botocore.exceptions import ClientError
from PIL import Image
import json
import numpy as np
import build_custom_model

AWS_S3_CREDS = {
    "aws_access_key_id":"*************",
    "aws_secret_access_key":"**************"
    }

sqs = boto3.client("sqs", region_name='us-east-1', **AWS_S3_CREDS)

response_queue = "https://sqs.us-east-1.amazonaws.com/************"
requestQueue = "https://sqs.us-east-1.amazonaws.com/**************"

class Student:
    """Encapsulates an Amazon DynamoDB table of student data."""
    def __init__(self, dyn_resource, table):
        """
        :param dyn_resource: A Boto3 DynamoDB resource.
        """
        self.dyn_resource = dyn_resource
        self.table = table

    def get_student(self, name):
        """
        Gets student data from the table for a specific student.

        :param name: The name of student.
        :return: The data about the requested student.
        """
        try:
            response = self.table.get_item(Key={'name': name})
        except ClientError as err:
            print(
                "Couldn't get student %s from table %s. Here's why: %s: %s",
                name, self.table.name,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
        else:
            return response['Item']


def base64_to_image(image_name, data):
    base64_data = data.encode('utf-8')
    with open(image_name, "wb") as fh:
        fh.write(base64.decodebytes(base64_data))


def send_to_queue(message):
    #===============================================================================================
    # SQS Response QUEUE

    response = sqs.send_message(
        QueueUrl=response_queue,
        MessageBody=message
    )
    print(f"Result sent to queue: {message}")


def build_cust_model():
    labels_dir = "./checkpoint/labels.json"
    model_path = "./checkpoint/model_vggface2_best.pth"

    # read labels
    with open(labels_dir) as f:
        labels = json.load(f)
    print(f"labels: {labels}")

    device = torch.device('cpu')
    model = build_custom_model.build_model(len(labels)).to(device)
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu'))['model'])

    return (labels, device, model)

def receive_message():
    messages = []
    response = sqs.receive_message(
        QueueUrl=requestQueue,
        MaxNumberOfMessages=1,
    )
    for message in response.get("Messages", []):
        messages.append(message)
    return messages

def process(img_path, labels, device, model):
    #====================+====================+====================+====================+
    # IMAGE Prediction

    print(f"Processing Image {img_path}")
    img = Image.open(img_path)
    img_tensor = transforms.ToTensor()(img).unsqueeze_(0).to(device)
    outputs = model(img_tensor)
    _, predicted = torch.max(outputs.data, 1)
    result = labels[np.array(predicted.cpu())[0]]
    
    img_name = img_path.split("/")[-1]
    img_and_result = f"({img_name}, {result})"
    print(f"Image and its recognition result is: {img_and_result}")

    return (img_name, result)


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('student_data')
        
    student = Student(dynamodb, table)

    results = {}
    labels, device, model = build_cust_model()
    i = 0
    # Receive pushed Images from new SQS trigger
    #==============================================================
    for msg_num, record in enumerate(event["Records"]):
        data = record["body"]
        print("Copying image to temp_file")
        tmp_img_dir = "/tmp/images/"
        if not os.path.exists(tmp_img_dir):
            os.mkdir(tmp_img_dir)
        data = json.loads(data)
        file_name = data['image_name']
        file_path = f"/tmp/images/{file_name}"
        base64_to_image(file_path, data['image_data'])
        pred_res = process(file_path, labels, device, model)
        result = student.get_student(name=pred_res[1])
        result['file_name'] = pred_res[0]
        send_to_queue(json.dumps(result))
        results[file_name] = result
        os.remove(file_path)
        i += 1
     
    print(f"No more messages found in the Queue. This Lambda Instance has processed {i} images in total")
    
    res = {
        "statusCode": 200,
        "body": json.dumps(
            results
        ),
    }
    return res