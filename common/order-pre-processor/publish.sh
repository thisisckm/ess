aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 824775819187.dkr.ecr.eu-west-2.amazonaws.com
docker build -t erp-uk-v1-order-pre-processor .
docker tag erp-uk-v1-order-pre-processor:latest 824775819187.dkr.ecr.eu-west-2.amazonaws.com/erp-uk-v1-order-pre-processor:latest
docker push 824775819187.dkr.ecr.eu-west-2.amazonaws.com/erp-uk-v1-order-pre-processor:latest
docker image rm 824775819187.dkr.ecr.eu-west-2.amazonaws.com/erp-uk-v1-order-pre-processor:latest
