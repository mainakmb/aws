#!/bin/python3

# Import boto3, os
import boto3
import os

s3Resource = boto3.resource('s3')
s3Client = boto3.client('s3')
response = s3Client.list_buckets()


# s3 delete old backups
def s3backupManage():
    # Set and Get Env variables
    value = int(os.getenv('BACKUP_WINDOW'))
    if type(value) != int:
        print("Environment Variable Error")
        exit()

    s3bucket = s3Resource.Bucket('**bucket-name**')

    # List all objects with .tar
    obj = s3bucket.objects.all()
    tar_list = []
    for i in obj:
        if i.key.endswith('.tar'):
            tar_list.append(i.key)
    new_tar_lst = tar_list[:len(tar_list) - value]

    # Delete .tar Object
    for new_obj in new_tar_lst:
        s3Resource.Object('**bucket-name**', new_obj).delete()


# Main function
if __name__ == "__main__":
    s3backupManage()
