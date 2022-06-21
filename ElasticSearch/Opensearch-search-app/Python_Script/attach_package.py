import boto3, sys, time

package_id = sys.argv[1]
domain_name = sys.argv[2]

client = boto3.client('opensearch', region_name="us-west-2")

response = client.associate_package(
    PackageID=package_id,
    DomainName=domain_name
)

time.sleep(30)