# Facial-Regonition-Edge
Distributed application that utilizes PaaS technologies and IoT platforms to perform real time facial recognition.
---
![image](https://user-images.githubusercontent.com/33671457/228112776-e956adcf-10e6-4884-a7ac-f70feac37939.png)
---
# Facial Recognition Software as a Service (SaaS) README

## Table of Contents

1. [Introduction](#introduction)
2. [Problem Statement](#problem-statement)
3. [Design and Implementation](#design-and-implementation)
   - [Architecture](#architecture)
   - [Autoscaling](#autoscaling)
4. [Testing and Evaluation](#testing-and-evaluation)
5. [Code](#code)
   - [main.py](#mainpy)
   - [web_helper.py](#web_helperpy)
   - [load_balancer.py](#load_balancerpy)
   - [worker.py](#workerpy)
   - [requirements.txt](#requirementstxt)
   - [worker_requirement.txt](#worker_requirementtxt)
6. [Installation and Running](#installation-and-running)

## 1. Introduction <a name="introduction"></a>

Since first explored in the 1960s, facial recognition software is no longer considered a novelty in today's technologically advanced world, as they are now standard and expected. Many people are familiar with this software and expect it in the context of unlocking personal devices, getting access to secure apps, and aiding to tag friends on social media platforms. There are many fewer known ways this software is being used. Corporations can use it for things such as smart advertising to aid in sales, organizations such as schools and churches can use it for tracking attendance, and it can also be used to save lives when police have it to aid in finding missing people and criminals. Every day people are coming up with new ideas and find new ways to incorporate them into our lives.

## 2. Problem Statement <a name="problem-statement"></a>

The many ways facial recognition software and the potential of how it can be used have caused an exponentially increasing demand for them. Although not all companies and people who want to use this valuable software have the knowledge or ability to create it. Thus, the emergence of facial recognition is an offered SaaS (Software as a Service). A successful robust facial recognition software service should have accuracy, use-case flexibility, on-demand usage, broad network access, dependability, and cost-effective metering. This project explores creating a facial recognition program that utilizes Amazon’s Cloud Computing Services combined with Dr. Zhao’s machine learning model, provided as an AMI (Amazon Machine Image), that satisfies many of the above characteristics.

## 3. Design and Implementation <a name="design-and-implementation"></a>

For this project, facial recognition application is supplied by Dr. Zhao, a professor from Arizona State University, in a previously trained deep learning model provided in an AMI. Dr. Zhao set the use-case criteria of input format and output format eliminating the need for use-case flexibility. Although this project does not address charging users, Amazon’s services are all measured, allowing easy tracking of usage costs which can then be used in calculating profitable but fair prices for the use of this software. The heterogeneous device support component of broad network access is not directly addressed in this project but can be implemented by creating a user interface. This user interface would have to be compatible with many devices, standardize users’ input images, and be secure to protect user information. Although device limitations due to computing capabilities and the availability of capabilities, components of the broad network are addressed through AWS EC2 instances. In Architecture we discuss the flow of our app and show how the remaining characteristics are addressed through utilizing AWS, showcasing how powerful cloud computing services can be.

### 4. Testing and Evaluation
When testing we are considering four main criteria: correct output, correct S3 bucket contents, correct EC2 autoscaling, and quick processing times. We used the face dataset, image expected output dataset, and workload generator provided by Dr. Zhao to test all four criteria.

1. **Correct Output**: Every provided user image must return the correct face recognition result as output.
2. **Correct S3 Bucket Contents**: Both the input and output buckets are correct.
   - The input bucket is satisfied if every user-provided image is stored with a key in the form of .jpg and the value is the image file.
   - The output bucket is satisfied if for every user-provided image there is a corresponding result with the key as the image name and the value as a string with the corresponding user's name.
3. **Correct EC2 Autoscaling**: The number of instances processing images is correct according to the workload.
4. **Quick Processing Time**: Our app can process 100 concurrent requests in five or fewer minutes.

### 5. Code
a. `main.py`
   - This file's purpose is to act as the main component of the web tier. When run, it hosts the REST API used to upload images under the endpoint "/upload" with the parameter "myfile".

b. `web_helper.py`
   - This file's purpose is to feed the script in `main.py` by scanning the response queue for available messages.

c. `load_balancer.py`
   - This file's purpose is to continually check for messages from the Request Queue, make a list of available worker nodes, start worker nodes, and pass the data from those messages to the worker nodes.

d. `worker.py`
   - This script is present on every worker node and is used to process received messages from the load balancer.

e. `requirements.txt`
   - Requirements file used to install needed Python packages for the Load Balancer and Web Tier.

f. `worker_requirement.txt`
   - Requirements file used to install needed Python packages for the worker nodes.

### 6. Installation and Running
a. All of the submitted files must be on the Web Tier EC2 instance.

b. The `requirements.txt` must be installed (via pip) on the Web Tier and the `worker_requirements.txt` must be installed (via pip) on each worker node.

c. From there, our group ssh into the Web Tier instance and creates three virtual terminals (using tmux).

d. After all necessary libraries are installed, all scripts are in their proper directories, and the three operating scripts are run, the system can begin taking requests concurrently.
