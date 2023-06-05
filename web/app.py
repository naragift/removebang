# TODO: refactor this single-file app into a package
import os
import pika
import binascii
import redis

from flask import Flask, abort, render_template, request, redirect, url_for
from google.cloud import storage

app = Flask(__name__)
app.config['BUCKET_NAME'] = os.environ.get('BUCKET_NAME', 'remove-bang')
rc = redis.Redis.from_url(os.environ.get(
    'REDIS_URL', 'redis://localhost:6379'))
storage_client = storage.Client()
queue_name = 'rb_jobs'
bucket = storage_client.bucket(app.config['BUCKET_NAME'])
rabbitmq_url = os.environ.get('RABBITMQ_URL', 'amqp://localhost')


def send_to_rabbitmq(job_id):
    connection = pika.BlockingConnection(
        pika.URLParameters(rabbitmq_url))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    channel.basic_publish('',
                          routing_key=queue_name,
                          body=job_id)


def send_job(file):
    job_id = binascii.hexlify(os.urandom(16)).decode()
    blob = bucket.blob(job_id)
    blob.content_type = file.content_type

    with blob.open('wb') as f:
        f.write(file.read())

    redis_key = f'rb:{job_id}'
    rc.set(redis_key, 'pending', ex=15*60)
    send_to_rabbitmq(job_id)
    return job_id


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        # TODO: validate filename, filter extensions!
        if not file:
            return 'No file uploaded, try again'
        job_id = send_job(file)
        return redirect(url_for('result', job_id=job_id))

    return render_template('index.html')


@app.route('/job/<job_id>')
def job_status(job_id):
    redis_key = f'rb:{job_id}'
    status = rc.get(redis_key)
    if not status:
        abort(404)
    status = status.decode()
    ready = status == 'done'
    url = None
    if ready:
        blob = bucket.blob(job_id)
        url = blob.public_url
    return {'ready': ready, 'url': url}


@app.route('/result/<job_id>')
def result(job_id):
    return render_template('result.html', job_id=job_id)


if __name__ == '__main__':
    app.run(port=7000, debug=True)
