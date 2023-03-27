FROM public.ecr.aws/lambda/python:3.8

ARG TORCH_HOME="/tmp/"
ENV TORCH_HOME=${TORCH_HOME}

COPY build_custom_model.py eval_face_recognition.py ./

# COPY data ./data

COPY requirements.txt ./

RUN python3.8 -m pip install -r requirements.txt -t .

COPY models ./models

COPY checkpoint ./checkpoint

COPY app.py ./

COPY __pycache__ ./

# Command can be overwritten by providing a different command in the template directly.
CMD ["app.lambda_handler"]