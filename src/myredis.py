from datetime import timedelta
import json
import redis
import yaml

# Reading the configuration from YAML file
with open('conf/conf.yaml', 'r') as file:
    config = yaml.safe_load(file)

redis_config = config['redis']

# Initialize the Redis Client
redis_client = redis.Redis(
    host=redis_config['host'],
    port=redis_config['port'],
    password=redis_config['password'],
    username=redis_config['username']
)

def set(key, value):
    redis_client.set(key, value, ex=timedelta(days=30))

def get_raw(key) -> [None, str]:
    val = redis_client.get(key)
    if val is None:
        return None
    else:
        return val.decode()


# Example usage
if __name__ == '__main__':
    # Testing Redis connection
    redis_client.set('test_key', 'Hello Redis')
    value = redis_client.get('test_key')
    print(f'The value for "test_key" is: {value.decode("utf-8")}')
