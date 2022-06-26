import boto3
import os

path_1 = os.getcwd()
path_2 = os.path.join(path_1, "raw_data")

print(__name__)
s3_client = boto3.client('s3')


print("yes")
for root, dirs, files in os.walk(path_2):
    for file in files:
        s3_client.upload_file(os.path.join(root, file), 'lmsbucket2022', file)
