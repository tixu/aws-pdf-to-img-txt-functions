#!/bin/bash
echo 'deleting zip file';
rm handler.zip ; 
echo 'zipping archive'
zip -r handler.zip *;
echo 'uploading function'
aws --profile user s3 cp handler.zip s3://lambdazip2;
echo 'deploying function'
aws lambda update-function-code --s3-bucket lambdazip2 --s3-key handler.zip --function-name ocr-one-python  --region eu-central-1 --profile user

