# Importing boto3, pickle
import boto3
import _pickle as pickle

# Creating the connection
ec2Client = boto3.client('ec2',
                         region_name='ap-south-1'
                         )
ec2 = boto3.resource('ec2',
                     region_name='ap-south-1',
                     )


# Checking what instances are running and specs
def printInstances():
    instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    for instance in instances:
        inst_names = [tag['Value'] for tag in instance.tags if tag['Key'] == 'Name']
        print(inst_names, instance.id, instance.cpu_options, instance.instance_type, instance.architecture, instance.image_id,
              instance.key_name)  # Print Instance name, ID, CPU Spec, CPU Architecture, AMI ID, ssh-key name


# Generating ssh-key pairs
def sshKeyGen():
    outfile = open('id_rsa_mainak.pem', 'w')
    key_pair = ec2.create_key_pair(KeyName='id_rsa_mainak')
    KeyPairOut = key_pair.key_material
    print(str(KeyPairOut))
    outfile.write(KeyPairOut)
    outfile.close()


# Launch an instance
def launchInstance():
    print("Input 1 for Intel instance \n"
          "Input 2 for ARM instance")
    num_input = int(input())
    if num_input == 1:
        ami_id = 'ami-0c1a7f89451184c8b'
        instance_type = 't2.medium'
        vm_name = 'intel-vm'
    elif num_input == 2:
        ami_id = 'ami-0d18acc6e813fd2e0'
        instance_type = 't4g.medium'
        vm_name = 'arm-vm'
    else:
        exit()
    instance_list1 = ec2.create_instances(ImageId=ami_id,
                                          MinCount=1,
                                          MaxCount=1,
                                          InstanceType=instance_type,
                                          KeyName='id_rsa_mainak',
                                          TagSpecifications=[
                                              {
                                                  'ResourceType': 'instance',
                                                  'Tags': [{
                                                      'Key': 'Name',
                                                      'Value': vm_name
                                                  }]
                                              }
                                          ],
                                          BlockDeviceMappings=[
                                              {
                                                  'DeviceName': '/dev/sda1',
                                                  'Ebs': {
                                                      'DeleteOnTermination': True,
                                                      'VolumeSize': 50,
                                                      'VolumeType': 'standard'
                                                  },
                                              },
                                          ]
                                          )
    instance_list1[0].wait_until_running()  # Waiting to launch before assigning the elastic IP address
    eip = ec2Client.allocate_address(Domain='vpc')
    print(eip)
    with open('allocation.txt', 'wb') as f:
        pickle.dump(eip, f)
    with open('instance_id.txt', 'wb') as f:
        pickle.dump(instance_list1[0].id, f)
    ec2Client.associate_address(
        InstanceId=instance_list1[0].id,
        AllocationId=eip["AllocationId"])


# Release Elastic IP
def releaseEip():
    with open("allocation.txt", 'rb') as f:
        eip = pickle.load(f)
    print(eip)
    ec2Client.release_address(AllocationId=eip['AllocationId'])
    print('Address released')


# Terminate Instances
def termInstance():
    with open("instance_id.txt", 'rb') as f:
        i_id = pickle.load(f)
    ec2Client.terminate_instances(InstanceIds=[i_id])
    print("Instance Terminated")


# Main function
if __name__ == "__main__":
    print("Input 1 for List all VMs, Template IDs and CPU architectures \n"
          "Input 2 for generate public and private key pairs \n"
          "Input 3 for Launching VM Instance \n"
          "Input 4 for Release Elastic IP \n"
          "Input 5 for Delete VM ")
    num = int(input())
    if num == 1:
        printInstances()
    elif num == 2:
        sshKeyGen()
    elif num == 3:
        launchInstance()
    elif num == 4:
        releaseEip()
    elif num == 5:
        termInstance()
    else:
        exit()
