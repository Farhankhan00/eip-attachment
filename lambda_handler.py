import boto3
from os import getenv


def lambda_handler(json_input, context):
    
    ec2 = boto3.client("ec2", region_name=json_input['region'])
    tag_key = getenv('TAGKEY')

    eips = find_tagged_eips(
        ec2, 
        tag_key,
        json_input['detail']['AutoScalingGroupName']
    )
    print(eips)

    avail_eips = sort_attached_eips(eips)

    print(avail_eips)

    assoc = attach_eip(
        ec2,
        json_input['detail']['EC2InstanceId'],
        avail_eips[0]['AllocationId']
    )
    print(assoc)


def find_tagged_eips(client, tag_key, tag_value):
    filters = [ 
        {
            'Name':'tag:{}'.format(tag_key),
            'Values':['{}'.format(tag_value)]
        }
    ]
    
    return client.describe_addresses(Filters=filters)['Addresses']

def attach_eip(client, instanceid, allocid):
    return client.associate_address( 
        AllocationId=allocid,
        InstanceId=instanceid 
    ) 
    

def sort_attached_eips(addresses):
    avail_eips = []
    for address in addresses: 
        if 'InstanceId' in address: 
            print('EIP {} is already attached to instanceid {}'.format(
                address['PublicIp'],
                address['InstanceId']
            ))
        else: 
            print('eip {} has no association'.format(address['PublicIp']))
            avail_eips.append(address)
    return avail_eips

if __name__ == '__main__':
    lambda_handler({}, {})
