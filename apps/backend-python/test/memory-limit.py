import requests
import docker
import time

# Setup Docker client
client = docker.from_env()

# Replace 'localhost' with the domain where your FastAPI app is hosted
BASE_URL = "http://localhost:8000"
CONTAINER_NAME = 'svelte-manga-api'  # Replace with your actual container name

def send_memory_intensive_request():
    container = client.containers.get(CONTAINER_NAME)
    memory_limit = 200 * 1024 * 1024  # 200MB in bytes
    print(f"Memory limit: {memory_limit / (1024 * 1024):.2f} MB")

    # Monitor the container PID to detect a restart
    initial_pid = container.attrs['State']['Pid']
    print(f"Initial PID: {initial_pid}")

    memory_usage_before = container.stats(stream=False)['memory_stats']['usage']
    print(f"Memory before: {memory_usage_before / (1024 * 1024):.2f} MB")

    try:
        # Loop to send requests until we reach the memory limit
        while True:
            # Send a request to the memory-intensive endpoint
            response = requests.get(f"{BASE_URL}/test-memory")
            print(f"Request to /test-memory: {response.status_code} {response.reason}")

            # Check memory usage after the request
            current_stats = container.stats(stream=False)
            memory_usage = current_stats['memory_stats']['usage']
            print(f"Current memory usage: {memory_usage / (1024 * 1024):.2f} MB")

            # Break the loop if we've hit the memory limit or the container has restarted
            if memory_usage >= memory_limit or container.attrs['State']['Pid'] != initial_pid:
                break

            time.sleep(1)  # Wait a bit before the next request

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

    # Final status check
    container.reload()
    if container.attrs['State']['Pid'] != initial_pid:
        print(f"The container has been restarted. New PID: {container.attrs['State']['Pid']}")
    else:
        print(f"The container did not restart. Current PID: {container.attrs['State']['Pid']}")

send_memory_intensive_request()
