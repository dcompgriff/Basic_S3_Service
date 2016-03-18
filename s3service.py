import boto3
from flask import Flask, jsonify
from botocore import exceptions

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('aws_config.py')

# app.config['SECRET_KEY']

s3 = boto3.client('s3',
                  aws_access_key_id=app.config['ACCESS_KEY'],
                  aws_secret_access_key=app.config['SECRET_KEY'])

@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/s3service/get-base64-string/<string:bucket_name>/<string:key>', methods=['GET'])
def get_base64_string(bucket_name, key):
    print "get-base64-string"
    bucket = get_bucket(bucket_name)

    # if the bucket doesn't exist, return a 404 error
    if not bucket:
        return jsonify({'error': 404})

    value = s3.Object(bucket_name, key).get().read().decode("Base64")
    return jsonify({'bucket': bucket_name, 'key': key, 'value': value})


@app.route('/s3service/put-base64-string/<string:bucket_name>/<string:key>/<string:value>', methods=['GET'])
def put_base_64_string(bucket_name, key, value):
    print "put-base64-string"
    try:
        bucket = get_bucket(bucket_name)
    except Exception as e:
        print e

    # if the bucket doesn't exist, make one
    if not bucket:
        s3.create_bucket(Bucket=bucket_name)

    s3.Object(bucket_name, key).put(Body=value)
    return jsonify({'bucket': bucket_name, 'key': key, 'value': value})


@app.route('/s3service/delete')
def delete():
    return ''


def get_bucket(bucket_name):
    bucket = s3.Bucket(bucket_name)

    try:
        s3.meta.client.head_bucket(Bucket=bucket_name)
    except exceptions.ClientError as e:
        # if it was a 404 error, the bucket doesn't exist
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:
            bucket = False

    return bucket

if __name__ == '__main__':
    app.run()
