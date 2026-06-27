FROM public.ecr.aws/lambda/python:3.9

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ ./app/
COPY lambda/ ./lambda/

CMD ["lambda.analyze.handler.lambda_handler"]
