# Create Stack For Importing Your Resources
# IDENTIFIER_FILE : Imported Resourses' Identifier
aws cloudformation create-change-set\
    --region {REGION_NAMWE} \
    --stack-name {STACK_NAME} \
    --change-set-name {CHANGE_SET_NAME} \
    --change-set-type IMPORT \
    --resources-to-import {IDENTIFIER_FILE_URL} \
    --capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND\
    --template-url {S3_HTTP_URL_STACK_TEMPLATE-network_resource.yaml}

# Execute Stack For Importing Your Resources
# Acutual Action For Importing Your Resources
# STACK_NAME, CHANGE_SET_NAME should be same with `create-change-set` Command
aws cloudformation execute-change-set \
    --region {REGION_NAMWE} \
    --stack-name {STACK_NAME} \
    --change-set-name {CHANGE_SET_NAME}

# Create Stack For Updating Your Resources
# Parameter Description
# KeyName : Your Pem Key Name
# ExpiryDate : Resource Expiry date (optional)
# MyIp : Current Your IP
# MasterUser : Opensearch Master User Name
# MasterPW : Opensearch Master Password
# OpenSearchDN : Opensearch Domain Name
aws cloudformation create-change-set \
    --region {REGION_NAMWE} \
    --stack-name {STACK_NAME} \
    --change-set-name {CHANGE_SET_NAME} \
    --role-arn {CLOUDFORMATION_ROLE_ARN} \
    --capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND \
    --parameters ParameterKey=KeyName,ParameterValue={YOUR_PEM_KEY} \
    ParameterKey=ExpiryDate,ParameterValue=$(date --date="2 days" +%Y-%m-%d) \
    ParameterKey=MyIp,ParameterValue=$(curl ipinfo.io/ip)/32 \
    ParameterKey=MasterUser,ParameterValue=master \
    ParameterKey=MasterPW,ParameterValue='Bespin12!' \
    ParameterKey=OpenSearchDN,ParameterValue=search-app \
    --change-set-type UPDATE \
    --template-url {S3_HTTP_URL_STACK_TEMPLATE-main_es_diy.yaml}

# Execute Stack For Updating Your Resources
# Acutual Action For Updating Your Resources
# STACK_NAME, CHANGE_SET_NAME should be same with `create-change-set` Command
aws cloudformation execute-change-set \
    --region {REGION_NAMWE} \
    --stack-name {STACK_NAME} \
    --change-set-name {CHANGE_SET_NAME}

# Cancel Stack For Updating Your Resources
aws cloudformation cancel-update-stack --stack-name {STACK_NAME} --region {REGION_NAMWE}

# Delete Stack
aws cloudformation delete-stack --stack-name {STACK_NAME} --region {REGION_NAMWE}