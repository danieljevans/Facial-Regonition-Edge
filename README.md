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

For this project, facial recognition application is supplied by Dr. Zhao, a professor from Arizona State University, in a previously trained deep learning model provided in an AMI. Dr. Zhao set the use-case criteria of input

