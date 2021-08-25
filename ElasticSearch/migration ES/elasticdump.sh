#! /bin/sh

/home/ec2-user/node_modules/elasticdump/bin/elasticdump\
  --s3AccessKeyId "{access_key}" \
  --s3SecretAccessKey "{secret_key}" \
  --input=http://{master private ip}:9200/{index_name} \
  --output "s3://{bucket_name}/{path}/{target_name}"\
  --limit=10000 \
  --httpAuthFile={file_path}