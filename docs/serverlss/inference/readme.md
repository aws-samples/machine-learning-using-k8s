AWS launched [Fargate](https://aws.amazon.com/fargate/) in 2017, which allows you to run containers without having to manage servers or clusters. If you have have inference application packed inside container you can build a serverless inference serving using AWS Fargate.

## Follow the below steps to create a serverless inference service
1. Container: You will need a container which has your trained model into it. Alternatively you can take standard serving container (e.g. tensorflow/serving) and add model in command when you start model server, which I did below.

1. Cluster: Let’s create the Fargate cluster by running the below command or you can use default cluster. Its just a logical entity we have not created any resources yet.
  ```
   aws ecs create-cluster --cluster-name fargate-cluster

  ```

1. Task definition: In order to run your container in Fargate you have to prepare the task definition. Basically a task definition is configuration file where you specify your container, resource limit and command you want to run inside the container. You can also use task definition to connect your container to other AWS services. You can see many task definition example [here](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/example_task_definitions.html). 

A complete task definition is present `docs/serverlss/inference/task.json`. I’ve used an official TensorFlow serving container and added a very simple model called half plus two, which takes a number and divides it by two and adds two.

1. Register the task: By running below command, you will receive arevision id of task which is required while creating a service.
  ```
  aws ecs register-task-definition --cli-input-json    file://task.json
  ```

1. Create the service: Lets create the service by running the below command. Update your security groups and subnets in below commands. Make sure that your security group allow inbound traffic for the port your service is available. You can control the number of container you want to run by changing ‘desired-count’.
   ```
   aws ecs create-service --cluster fargate-cluster
                       --service-name tensorflow_inference 
                       --task-definition FargateTFInference:1 
                       --desired-count 1 
                       --launch-type "FARGATE" 
                       --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxx],securityGroups=[sg-yyyy], assignPublicIp='ENABLED'}"
   ```
   Above command will create a service called tensorflow_inference. A difference between service and task is available [here](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/Welcome.html). An ECS service under the hood creates a task, so basically a service a task running forever. 

1. Get the external IP: Goto ECS cluster fargate-cluster → under service you will see service called tensorflow_inference → click on it, there will tab called Tasks which will have running tasks list. Click on task and you will have public ip associated with it.

1. Run Inference: Lets run a very simple inference
   ```
   curl -d '{"instances": [1.0, 2.0, 5.0]}' -X POST http://<external_ip>:8501/v1/models/saved_model_half_plus_two:predict

   {
       "predictions": [2.5, 3.0, 4.5]
   }

   ```

