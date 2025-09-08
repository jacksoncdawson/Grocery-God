"""
Defines an AWS Lambda handler for executing the Safeway data pipeline and uploading its output to an S3 bucket.

The handler function runs the Safeway pipeline, stores the resulting file in a temporary directory, and uploads it to a specified S3 bucket and prefix. The S3 bucket and prefix are configured via environment variables 'OUTPUT_BUCKET' and 'OUTPUT_PREFIX'. The function returns a dictionary containing the S3 bucket name, object key, and the local temporary file path.

Dependencies:
- boto3: For interacting with AWS S3.
- pathlib: For file path manipulations.
- grocery_god.pipelines.safeway: Contains the pipeline logic.

Environment Variables:
- OUTPUT_BUCKET: Name of the S3 bucket to upload the output.
- OUTPUT_PREFIX: Prefix (folder path) in the S3 bucket for the uploaded file.
"""

import os
import boto3
import pathlib

from grocery_god.pipelines.safeway import run_safeway_pipeline

s3 = boto3.client("s3")

BUCKET = os.getenv("OUTPUT_BUCKET")
PREFIX = os.getenv("OUTPUT_PREFIX")

def handler(event, context):
    final_path = run_safeway_pipeline(output_path="/tmp")

    filename = pathlib.Path(final_path).name

    key = f"{PREFIX}{filename}"

    s3.upload_file(final_path, BUCKET, key)

    return {"bucket": BUCKET, "key": key, "tmp_path": str(final_path)}
