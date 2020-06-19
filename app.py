from __future__ import absolute_import
import time
from flask import Flask, render_template, request, redirect, url_for
# from flask_sqlalchemy import SQLAlchemy
from celery import Celery
from kombu import Queue,Exchange

#实例化Flask
app = Flask(__name__)
#配置
# app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'    
app.config['CELERY_BROKER_URL'] = 'amqp://guest:guest@localhost:5672/test'  #使用Rabbitmq作为BROKER
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'      #redis作为数据返回
app.config['CELERY_ACKS_LATE'] = True
app.config['CELERYD_PREFETCH_MULTIPLIER'] = 1   
# app.config['CELERYD_CONCURRENCY'] = 20
#设置优先级队列
app.config['CELERY_QUEUES'] = (
    Queue(name="celery", exchange=Exchange("celery"), routing_key="celery"), 
    Queue(name="celery_priority", exchange=Exchange("celery_priority"), routing_key="celery_priority",queue_arguments={'x-max-priority':9})
) #设置队列优先级为9
# app.config['CELERYD_MAX_TASKS_PER_CHILD'] = 200


#实例化celery
celeryapp = Celery(broker=app.config['CELERY_BROKER_URL'])
celeryapp.conf.update(app.config)


#设置两个函数方便观察
@celeryapp.task
def add(x, y):
    z = x + y
    time.sleep(20)
    print(z)
    return z

@celeryapp.task
def muti(x, y):
    z = x * y
    time.sleep(20)
    return z


@app.route('/', methods=['GET', 'POST'])
def hello_world():
    #显示html内容,当有GET请求时调用函数
    if request.method == 'GET':
        add.apply_async((1,1),queue='celery_priority',priority=1)   #调用函数放进同一个queue中并设置优先级大小，0-9递增
        muti.apply_async((2,2),queue='celery_priority',priority=9)
        add.apply_async((3,3),queue='celery_priority', priority=5)
        return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
