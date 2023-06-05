import io
import os
import sys
import time

from google.cloud import storage
import pika
import pika.exceptions
import redis
import replicate
import requests


bucket_name = os.environ.get('BUCKET_NAME', 'remove-bang')
rc = redis.Redis.from_url(os.environ.get(
    'REDIS_URL', 'redis://localhost:6379'))
storage_client = storage.Client()
queue_name = 'rb_jobs'
replicate_api_token = os.environ.get('REPLICATE_API_TOKEN',
                                     'r8_6pyc9R9vcIEdgEXjdG7DBnihm8xQD1n44699t')
replicate_client = replicate.Client(replicate_api_token)
rabbitmq_url = os.environ.get('RABBITMQ_URL', 'amqp://localhost')


def remove_background(image_io):
    """Returns the resulting output image URL as str"""
    output = replicate_client.run(
        'cjwbw/rembg:fb8af171cfa1616ddcf1242c093f9c46bcada5ad4cf6f2fbe8b81b330ec5c003',
        input={'image': image_io})
    return output


def process_job(job_id):
    # Get the job from Redis
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(job_id)
    image_io = io.BytesIO(blob.download_as_bytes())
    output_im_url = remove_background(image_io)

    # Upload the output image to GCS
    output_blob = bucket.blob(f'{job_id}')
    output_blob.upload_from_string(requests.get(
        output_im_url).content, 'image/png  ')  # type: ignore
    output_blob.make_public()

    # Update the job status in Redis
    rc.set(f'rb:{job_id}', 'done')


def main():
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.URLParameters(rabbitmq_url))
        except pika.exceptions.AMQPConnectionError:
            print('Connection failed, retrying...')
            time.sleep(3)
            continue
        else:
            break
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)

    def callback(ch, method, properties, body):
        job_id: str = body.decode()
        print(f'[x] Processing {job_id}')
        process_job(job_id)
        print(f'[x] Done processing {job_id}, sending ack')
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=queue_name,
                          on_message_callback=callback)

    channel.start_consuming()


try:
    print('[*] Starting background remover worker')
    main()
except KeyboardInterrupt:
    print('Interrupted')
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)
