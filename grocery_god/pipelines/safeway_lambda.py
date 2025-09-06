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

    return {"bucket": BUCKET, "key": key, "tmp_path": final_path}
