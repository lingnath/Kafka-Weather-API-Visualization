# Kafka-Weather-API-Visualization
This project streams real-time weather data from Weather API using Kafka. We visualize weather related data on a map.

### Limitations
1. We are collecting data from a publicly available source so security is not at the forefront of this project. For now, the IAM policies are lax. If this were not a personal project, I would have tightened the IAM policies significantly.
2. The accuracy of this project is based on how many weather stations there are in the area of interest and how frequently the data updates

## AWS Account
1. Create AWS account
2. Create IAM user with following policies attached ```AmazonS3FullAccess```
3. Create an access key for this user

## EC2
1. Create and/or use an EC2 t2.xlarge instance running on Ubuntu 24.04 with at least 16GB of EBS storage.
2. Ensure you create or use an existing key pair for login when setting up the EC2 instance
3. Under security group inbound rules, create or modify a security group with the following:
  - SSH Type (Port 22) from Source as MY IP
  - Port 8888 from Sources as MY IP
4. Attach this security group to your EC2 instance
5. Upload the files in this repository into your EC2 folder

## Software Installations
1. Go to ```Software_Installations``` folder
2. Run the following in bash
```bash
chmod +x install_docker_compose.sh
chmod +x install_docker.sh
chmod +x install_packages.sh
```
3. Run the following: ```./install_packages.sh```, ```./install_docker.sh```, ```./install_docker_compose.sh```

## Kafka Setup
1. Go to ```kafka_project``` folder
2. Create a .env file with the following:
```env
api_key=
ACCESS_KEY=
SECRET_KEY=
```
3. Then fill in the .env file accordingly
4. Fill in the ```config_file.toml``` accordingly as well
5. Run ```docker exec -it kafka bash```
6. Inside the Docker kafka container, run ```kafka-topics --create --topic weather-data --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1``` to create the Kafka topic
7. Run ```source /home/ubuntu/Software_Installations/python_env/bin/activate``` to start venv
8. After exiting the Docker kafka container, run ```python3 create_s3_buckets.py``` to create the S3 bucket that will store the streaming data

## Running Kafka
1. Go to ```kafka_project``` folder if you haven't done so already
2. Run ```docker-compose up -d``` to spin up Kafka
3. If you haven't done so already, run ```source /home/ubuntu/Software_Installations/python_env/bin/activate``` to start venv
4. After waiting for about 1 minute or so for Kafka to start, run ```python3 producer.py```
5. In another terminal, run ```source /home/ubuntu/Software_Installations/python_env/bin/activate``` again
6. Then in this other terminal, run ```python3 consumer.py```
7. Because streaming happens until the end of time, you will need to stop the producer and consumer manually. To do so, press ```Ctrl+C``` for either of them to stop the tasks
8. Once you are done, run ```docker-compose stop```

## Visualizing Data
1. Go to ```kafka_project``` folder if you haven't done so already
2. If you haven't done so already, run ```source /home/ubuntu/Software_Installations/python_env/bin/activate``` to start venv
3. Run ```jupyter notebook``` to start Jupyter Notebook. You should see a link to LocalHost in the terminal. Click on that link
4. Begin visualizing data on ```visualize_data.ipynb```
