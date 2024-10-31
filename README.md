# SMAIAX Backend Load Test

This is a simple load test for the SMAIAX backend. It uses the [Locust](https://locust.io/) load testing framework to simulate multiple users interacting with the backend.

## Prerequisites
Before running the load test, you need to have the SMAIAX backend running on your machine.
To run the backend start it with the following commands:

```bash 
docker compose build
```

```bash
docker compose up -d
```

To run the load test, you need to have Python installed on your machine. You can install the required dependencies by running the following command:

```bash
pip install -r requirements.txt
```

## Running the load test
You can run the load test by executing the following command:

```bash
locust -f locustfile.py
```

This will start a web server on `http://localhost:8089` where you can configure the number of users and the spawn rate for the load test.

