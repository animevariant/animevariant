import requests
import docker

# Setup Docker client
client = docker.from_env()

# Replace 'localhost' with the domain where your FastAPI app is hosted
BASE_URL = "http://localhost:8000"
CONTAINER_NAME = 'svelte-manga-api'  # Replace with your actual container name

# List of API endpoints to test
endpoints = [
    '/',
    '/api/manga',
    '/api/manga/manga-tf996688',
    '/api/manga/manga-tf996688/chapter-1',
    '/api/search?word=eternal',
    '/api/getimage?url=https%3A%2F%2Fcm.blazefast.co%2Fa4%2F45%2Fa4458a2fadf6cd005dc1a92a6ab8e4b3.jpg',
    '/api/mangaimage/manga-tf996688.jpg',
    '/api/a4/45/a4458a2fadf6cd005dc1a92a6ab8e4b3.jpg',
    '/metrics'
]

def send_requests_and_monitor_memory():
    container = client.containers.get(CONTAINER_NAME)
    stats_before = container.stats(stream=False)
    memory_usage_before = stats_before['memory_stats']['usage']
    print(f"Memory before requests: {memory_usage_before / (1024 * 1024):.2f} MB")

    # Send requests to the FastAPI application
    for endpoint in endpoints:
        full_url = BASE_URL + endpoint.format(manga_id='manga-tf996688', chapter_id='chapter-1')
        response = requests.get(full_url)
        if response.status_code == 200:
            print(f"Success: {endpoint}")
        else:
            print(f"Failed: {endpoint}")

    # Monitor memory usage after sending requests
    stats_after = container.stats(stream=False)
    memory_usage_after = stats_after['memory_stats']['usage']
    print(f"Memory after requests: {memory_usage_after / (1024 * 1024):.2f} MB")

    # Calculate the difference in memory usage
    difference = memory_usage_after - memory_usage_before
    print(f"Memory usage difference: {difference / (1024 * 1024):.2f} MB")

# Run the test
send_requests_and_monitor_memory()
