aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 824775819187.dkr.ecr.eu-west-2.amazonaws.com
docker build -t amazon-pull-order-v1 .
docker tag amazon-pull-order-v1:latest 824775819187.dkr.ecr.eu-west-2.amazonaws.com/amazon-pull-order-v1:latest
docker push 824775819187.dkr.ecr.eu-west-2.amazonaws.com/amazon-pull-order-v1:latest
docker image rm 824775819187.dkr.ecr.eu-west-2.amazonaws.com/amazon-pull-order-v1:latest
