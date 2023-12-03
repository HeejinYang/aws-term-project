import boto3
from botocore.exceptions import NoCredentialsError

def get_instance_name(instance):
    for tag in instance.get('Tags', []):
        if tag['Key'] == 'Name':
            return tag['Value']
    return 'No name'

def list_instances(ec2):
    try:
        response = ec2.describe_instances()
        reservations = response['Reservations']

        if reservations:
            print("Existing instances:")
            for reservation in reservations:
                for instance in reservation['Instances']:
                    instance_id = instance['InstanceId']
                    instance_name = get_instance_name(instance)
                    ami_id = instance['ImageId']
                    instance_type = instance['InstanceType']
                    state = instance['State']['Name']
                    monitoring_state = instance['Monitoring']['State']

                    print(f"[id] {instance_id}, [state] {state}, [Name] {instance_name}, [AMI] {ami_id}, [type] {instance_type}, [monitoring state] {monitoring_state}")
        else:
            print("No instances found.")

    except NoCredentialsError:
        print("Credentials not available. Please check your AWS credentials configuration.")
    except Exception as e:
        print(f"Error: {e}")


def start_instance(ec2, instance_id):
    try:
        ec2.start_instances(InstanceIds=[instance_id])
        print(f"Successfully started instance {instance_id}")
    except NoCredentialsError:
        print("Credentials not available. Please check your AWS credentials configuration.")
    except Exception as e:
        print(f"Error: {e}")

def start_all_instances(ec2):
    try:
        describe_instances_response = ec2.describe_instances()
        for reservation in describe_instances_response['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                instance_state = instance['State']['Name']

                if instance_state != 'terminated':
                    start_instance(ec2, instance_id)
                else:
                    print(f"Ignoring terminated instance {instance_id}")

    except NoCredentialsError:
        print("Credentials not available. Please check your AWS credentials configuration.")
    except Exception as e:
        print(f"Error: {e}")

def stop_instance(ec2, instance_id):
    try:
        ec2.stop_instances(InstanceIds=[instance_id])
        print(f"Successfully stopped instance {instance_id}")
    except NoCredentialsError:
        print("Credentials not available. Please check your AWS credentials configuration.")
    except Exception as e:
        print(f"Error: {e}")

def stop_all_instances(ec2):
    try:
        describe_instances_response = ec2.describe_instances()
        for reservation in describe_instances_response['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                instance_state = instance['State']['Name']

                if instance_state != 'terminated':
                    stop_instance(ec2, instance_id)
                else:
                    print(f"Ignoring terminated instance {instance_id}")

    except NoCredentialsError:
        print("Credentials not available. Please check your AWS credentials configuration.")
    except Exception as e:
        print(f"Error: {e}")

def available_zones(ec2):
    print("Available zones....")
    try:
        response = ec2.describe_availability_zones()
        zones = response['AvailabilityZones']

        for zone in zones:
            zone_id = zone['ZoneId']
            region_name = zone['RegionName']
            zone_name = zone['ZoneName']
            print(f"[id] {zone_id}, [region] {region_name}, [zone] {zone_name}")

        print(f"You have access to {len(zones)} Availability Zones.")

    except NoCredentialsError:
        print("Credentials not available. Please check your AWS credentials configuration.")
    except Exception as e:
        print(f"Error: {e}")

def available_regions(ec2):
    print("Available regions ....")
    try:
        response = ec2.describe_regions()
        regions = response['Regions']

        for region in regions:
            region_name = region['RegionName']
            endpoint = region['Endpoint']
            print(f"[region] {region_name}, [endpoint] {endpoint}")

    except NoCredentialsError:
        print("Credentials not available. Please check your AWS credentials configuration.")
    except Exception as e:
        print(f"Error: {e}")

def reboot_instance(ec2, instance_id):
    try:
        ec2.reboot_instances(InstanceIds=[instance_id])
        print(f"Successfully rebooted instance {instance_id}")

    except NoCredentialsError:
        print("Credentials not available. Please check your AWS credentials configuration.")
    except Exception as e:
        print(f"Error: {e}")


def list_images(ec2, ami_name):
    try:
        response = ec2.describe_images(Filters=[{'Name': 'name', 'Values': [ami_name]}])

        for image in response['Images']:
            image_id = image['ImageId']
            name = image['Name']
            owner_id = image['OwnerId']

            print(f"[ImageID] {image_id}, [Name] {name}, [Owner] {owner_id}")

    except NoCredentialsError:
        print("Credentials not available. Please check your AWS credentials configuration.")
    except Exception as e:
        print(f"Error: {e}")

def create_instance(ec2, ami_id):
    try:
        response = ec2.run_instances(
            ImageId=ami_id,
            InstanceType='t2.micro',
            MinCount=1,
            MaxCount=1
        )

        instance_id = response['Instances'][0]['InstanceId']

        print(f"Successfully started EC2 instance {instance_id} based on AMI {ami_id}")

    except NoCredentialsError:
        print("Credentials not available. Please check your AWS credentials configuration.")
    except Exception as e:
        print(f"Error: {e}")


def execute_command(instance_id, command):
    ssm_client = boto3.client('ssm')

    response = ssm_client.send_command(
        InstanceIds=[
            instance_id
        ],
        DocumentName="AWS-RunShellScript",
        Parameters={'commands': [command]},
    )

    command_id = response['Command']['CommandId']

    waiter = ssm_client.get_waiter('command_executed')
    waiter.wait(InstanceId=instance_id, CommandId=command_id)

    output = ssm_client.get_command_invocation(
        InstanceId=instance_id,
        CommandId=command_id,
    )['StandardOutputContent']

    return output

def terminate_instance(ec2, instance_id):
    try:
        response = ec2.terminate_instances(InstanceIds=[instance_id])
        print(f"Terminating instance {instance_id}")
        print(f"Termination response: {response}")
    except Exception as e:
        print(f"Error terminating instance {instance_id}: {e}")


def main():
    # EC2 클라이언트 생성
    ec2 = boto3.client('ec2')

    while True:
        print('\n')
        print("--------------------------------------------------------")
        print("1. List instances                2. Start instance")
        print("3. Stop instance                 4. available zones")
        print("5. available regions             6. reboot instance")
        print("7. list images                   8. create instance")
        print("9. start all instance            10. stop all instance")
        print("11. execute 'condor_status'      12. terminate instance")
        print("                                 99. Quit")
        print("--------------------------------------------------------")

        choice = input("Enter your choice (1-99): ")

        if choice == '1':
            list_instances(ec2)
        elif choice == '2':
            instance_id = input("Enter instance ID to start: ")
            start_instance(ec2, instance_id)
        elif choice == '3':
            instance_id = input("Enter instance ID to stop: ")
            stop_instance(ec2, instance_id)
        elif choice == '4':
            available_zones(ec2)
        elif choice == '5':
            available_regions(ec2)
        elif choice == '6':
            instance_id = input("Enter instance ID to reboot: ")
            reboot_instance(ec2, instance_id)
        elif choice == '7':
            ami_name = input("Enter AMI name to list: ")
            list_images(ec2, 'htcondor-worker')
        elif choice == '8':
            ami_id = input("Enter AMI ID to create an instance: ")
            create_instance(ec2, ami_id)
        elif choice == '9':
            start_all_instances(ec2)
        elif choice == '10':
            stop_all_instances(ec2)
        elif choice == '11':
            instance_id = input("Enter instance ID: ")

            #command = input("Enter shell command to execute: ")
            command = 'condor_status'
            result = execute_command(instance_id, command)
            print(f"Command Result on {instance_id}:\n{result}")
        elif choice == '12':
            instance_id = input("Enter instance ID to terminate: ")
            terminate_instance(ec2, instance_id)
        elif choice == '99':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter right number")


if __name__ == "__main__":
    main()

