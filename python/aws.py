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

                    print(f"[id] {instance_id}, [Name] {instance_name}, [AMI] {ami_id}, [type] {instance_type}, [state] {state}, [monitoring state] {monitoring_state}")
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


def stop_instance(ec2, instance_id):
    try:
        ec2.stop_instances(InstanceIds=[instance_id])
        print(f"Successfully stopped instance {instance_id}")
    except NoCredentialsError:
        print("Credentials not available. Please check your AWS credentials configuration.")
    except Exception as e:
        print(f"Error: {e}")


def main():
    # EC2 클라이언트 생성
    ec2 = boto3.client('ec2')

    while True:
        print()
        print("1. List instances")
        print("2. Start instance")
        print("3. Stop instance")
        print("4. Quit")

        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            list_instances(ec2)
        elif choice == '2':
            instance_id = input("Enter instance ID to start: ")
            start_instance(ec2, instance_id)
        elif choice == '3':
            instance_id = input("Enter instance ID to stop: ")
            stop_instance(ec2, instance_id)
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")


if __name__ == "__main__":
    main()

