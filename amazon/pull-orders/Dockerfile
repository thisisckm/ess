FROM public.ecr.aws/lambda/python:3.11
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt
COPY src/app.py ${LAMBDA_TASK_ROOT}
ADD src/system ${LAMBDA_TASK_ROOT}/system
CMD [ "app.handler" ]