# Kafka-Weather-API-Visualization
This project streams real-time weather data from Weather API using Kafka. We visualize weather related data on a map.

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
