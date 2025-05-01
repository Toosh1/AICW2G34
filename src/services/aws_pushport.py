import boto3, os, gzip, shutil, zipfile
from dotenv import load_dotenv

load_dotenv()

aws_access_key = os.getenv("AWS_ACCESS")
aws_secret_key = os.getenv("AWS_SECRET")

bucket_name = "darwin.xmltimetable"
prefix = "PPTimetable/"
store = "src/data/aws/"
extracted_store = os.path.join(store, "extracted")

# Ensure directories exist
os.makedirs(store, exist_ok=True)
os.makedirs(extracted_store, exist_ok=True)

# Create S3 client
s3 = boto3.client(
    's3',
    region_name='eu-west-1',
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key
)

if __name__ == "__main__":
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

    for obj in response.get('Contents', []):
        filename = os.path.basename(obj['Key'])
        download_path = os.path.join(store, filename)
        s3.download_file(bucket_name, obj['Key'], download_path)
        print(f"Downloaded {obj['Key']} to {download_path}")

        # Handle .gz files
        if filename.endswith(".gz"):
            extracted_path = os.path.join(extracted_store, filename[:-3])
            with gzip.open(download_path, 'rb') as f_in:
                with open(extracted_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            print(f"Extracted GZ to {extracted_path}")
            os.remove(download_path)
            print(f"Deleted {download_path}")

        # Handle .zip files
        elif filename.endswith(".zip"):
            with zipfile.ZipFile(download_path, 'r') as zip_ref:
                zip_ref.extractall(extracted_store)
            print(f"Extracted ZIP contents to {extracted_store}")
            os.remove(download_path)
            print(f"Deleted {download_path}")
