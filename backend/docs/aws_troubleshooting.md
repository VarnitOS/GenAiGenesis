# AWS S3 Troubleshooting

## Current Issue
The application is encountering "Access Denied" errors when attempting to connect to the configured S3 bucket. This document provides steps to resolve these permission issues.

## AWS S3 Access Denied Troubleshooting

1. **Verify IAM User Permissions**
   
   Your IAM user (with access key ID AKIAX2DZES53XM4CG4HR) needs the following permissions:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "s3:ListBucket",
           "s3:GetObject",
           "s3:PutObject",
           "s3:DeleteObject"
         ],
         "Resource": [
           "arn:aws:s3:::law-der--use1-az4--x-s3",
           "arn:aws:s3:::law-der--use1-az4--x-s3/*"
         ]
       }
     ]
   }
   ```

2. **Verify S3 Bucket Exists**
   
   Ensure the bucket `law-der--use1-az4--x-s3` exists in the `us-east-1` region.
   
   You can check this in the AWS Management Console or run:
   ```
   aws s3 ls --region us-east-1
   ```

3. **Check Bucket Policy**
   
   Ensure the bucket doesn't have a restrictive bucket policy that's denying access.

4. **Verify Bucket Ownership**
   
   Make sure the IAM user belongs to the AWS account that owns the S3 bucket.

5. **Check for Access Points**
   
   If the bucket is using S3 Access Points, you may need additional permissions.

## Next Steps

1. In the AWS Management Console, go to the IAM section
2. Find your user (the one associated with the access key AKIAX2DZES53XM4CG4HR)
3. Attach the appropriate S3 policy
4. If the bucket belongs to a different AWS account, you'll need cross-account access configured

## Temporary Workaround

The application has been configured to run with local storage (`S3_ENABLED=False`) until the AWS permissions are resolved. This allows you to continue development without interruption.

To enable S3 storage once permissions are fixed:
1. Update the `.env` file: Set `S3_ENABLED=True`
2. Run the test script again: `python3 scripts/test_aws_cli.py` to verify access 