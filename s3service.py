import sys
import boto3
import requests
from flask import Flask, jsonify
from botocore import exceptions

app = Flask(__name__, instance_relative_config=True)
s3 = boto3.resource('s3')

S3_URL = 'https://%s.s3.amazonaws.com/%s'


@app.route('/s3service/get-string/<string:bucket_name>/<string:key>', methods=['GET'])
def get_string(bucket_name, key):
    try:
        content = requests.get(S3_URL % (bucket_name, key)).content

        # if it's xml, that means the key wasn't found
        if content[0] == '<':
            return jsonify({'error': 'Key not found'})
        else:
            return jsonify({key: content})

    except Exception as e:
        return jsonify({'error': e})


@app.route('/s3service/put-string/<string:bucket_name>/<string:key>/<string:value>', methods=['GET'])
def put_string(bucket_name, key, value):
    bucket = get_bucket(bucket_name)

    # handle errors
    if isinstance(bucket, dict) and 'error' in bucket:
        # if the bucket doesn't exist, make one
        if bucket['error'] == 'Bucket does not exist':
            s3.create_bucket(Bucket=bucket_name)
        else:
            return jsonify(bucket)

    s3.Object(bucket_name, key).put(Body=value)
    return jsonify({'bucket': bucket_name, 'key': key, 'value': value})


def get_bucket(bucket_name):
    result = s3.Bucket(bucket_name)

    try:
        s3.meta.client.head_bucket(Bucket=bucket_name)
    except exceptions.ClientError as e:
        # if it was a 404 error, the bucket doesn't exist
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:
            result = {'error': 'Bucket does not exist'}
    except exceptions.NoCredentialsError as e:
        result = {'error': 'No credentials found'}
    except:
        result = {'error': sys.exec_info()[0]}

    return result


if __name__ == '__main__':
    app.run()
