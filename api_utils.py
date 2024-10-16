import time
import requests
from requests.exceptions import RequestException
from functools import wraps

def retry_api_call(max_retries=3, delay=5):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except RequestException as e:
                    retries += 1
                    if retries == max_retries:
                        raise Exception(f"API call failed after {max_retries} attempts: {str(e)}")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

@retry_api_call()
def make_api_request(url, method='GET', headers=None, data=None, json=None):
    response = requests.request(method, url, headers=headers, data=data, json=json)
    response.raise_for_status()
    return response
