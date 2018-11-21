#!/bin/bash 
echo erasing test file; 
aws --profile user s3 rm s3://telos-1/test.pdf; 
echo pushing file;
aws --profile user s3 cp ../page11.pdf s3://telos-1/scan/scan7/test.pdf

