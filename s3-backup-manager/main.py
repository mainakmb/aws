#!/bin/python3

# Import boto3, os
import boto3
import os

s3Resource = boto3.resource('s3')
s3Client = boto3.client('s3')
response = s3Client.list_buckets()


# s3 delete old backups according BACKUP_WINDOW
def s3backupManage():
    # Set and Get Env variables
    value = int(os.getenv('BACKUP_WINDOW'))
    if type(value) != int:
        print("Environment Variable Error")
        exit()

    s3bucket = s3Resource.Bucket('**bucket-name**')     # Add your bucket name

    # List all objects with .tar
    obj = s3bucket.objects.all()
    tar_list = []
    for i in obj:
        if i.key.endswith('.tar'):
            tar_list.append(i.key)
    
    # List unix_timestamp for sorting
    sort_id_list = []
    for j in tar_list:
      sort_id = int(j.split("_")[0])
      sort_id_list.append(sort_id)
    
    # Add unix_timestamp and full object name as key-value
    d = {}
    for k in range(len(tar_list)):
      d[sort_id_list[k]] = tar_list[k]
    sorted_d = sorted(d.items())
    temp_list = []
    for l in sorted_d:
      temp_list.append(l[1])

    final_delt_lst = temp_list[:len(temp_list) - value]

    # Delete .tar Object
    for new_obj in final_delt_lst:
      print(new_obj)
      s3Resource.Object('**bucket-name**', new_obj).delete()


# Main function
if __name__ == "__main__":
    s3backupManage()
