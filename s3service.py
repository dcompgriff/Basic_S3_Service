from flask import Flask, jsonify
import boto3
import botocore
import os

app = Flask(__name__)
s3 = boto3.resource('s3')

LOCAL_PATH = '~/s3/'


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/s3service/get/<string:bucket_name>/<string:key>', methods=['GET'])
def get(bucket_name, key):
    bucket = get_bucket(bucket_name)

    # if the bucket doesn't exist, return a 404 error
    if not bucket:
        return jsonify({'error': 404})

    # search the bucket for the desired file
    for k in bucket.objects.all():
        file_name = str(k.key)
        # if we found the key and it isn't already saved locally, download it
        if file_name == key and not os.path.exists(LOCAL_PATH + file_name):
            k.get_contents_to_filename(LOCAL_PATH + file_name)
            return jsonify({'path': LOCAL_PATH + file_name})

    return jsonify({'already_exists': LOCAL_PATH + file_name})


@app.route('/s3service/put/<string:bucket_name>/<string:file_path>', methods=['PUT'])
def put(bucket_name, file_path):
    bucket = get_bucket(bucket_name)

    # if the bucket doesn't exist, make one
    if not bucket:
        s3.create_bucket(Bucket=bucket_name)

    # make sure the file exists
    if not os.path.exists(file_path):
        return jsonify({'error': 'File does not exist'})

    # put the file in the bucket
    file_name = os.path.basename(file_path)
    s3.Object(bucket_name, file_name).put(Body=open(file_path, 'rb'))
    return jsonify({'bucket': bucket_name, 'key': file_name})


@app.route('/s3service/delete')
def delete():
    return ''


def get_bucket(bucket_name):
    bucket = s3.Bucket(bucket_name)

    try:
        s3.meta.client.head_bucket(Bucket=bucket_name)
    except botocore.exceptions.ClientError as e:
        # if it was a 404 error, the bucket doesn't exist
        error_code = int(e.response['Error']['Code'])
        if error_code == 404
            bucket = False

    return bucket

if __name__ == '__main__':
    app.run()
