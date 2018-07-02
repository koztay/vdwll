from math import sqrt
import re
import requests
from celery import Celery

# app = Celery('tasks', backend='redis', broker='redis://192.168.1.210:6379/0')
app = Celery('tasks', broker='amqp://kemal:123456@192.168.1.21:5672/videowall', backend='amqp')
# app.conf.CELERY_RESULT_BACKEND = "redis://192.168.1.210:6379/0"

html_link_regex = re.compile('<a\s(?:.*?\s)*?href=[\'"](.*?)[\'"].*?>')

@app.task
def sqrt_task(value):
    return sqrt(value)

@app.task
def fibo_task(value):
    a, b = 0, 1
    for item in range(value):
        a, b = b, a + b
    
    message = "The fibonacci calculated by worker %s was %d"\
        % (fibo_task.request.id, a)
    return (value, message)

@app.task
def crawl_task(url):
    request_data = requests.get(url)
    links = html_link_regex.findall(request_data.text)
    message = "The task %s found the following links %s.. " \
        % (crawl_task.request.id, links[0:2])
    return message
