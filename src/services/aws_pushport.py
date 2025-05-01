import boto3, os, gzip, shutil, zipfile
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS = os.getenv("AWS_ACCESS")
AWS_SECRET = os.getenv("AWS_SECRET")
BUCKET_NAME = "darwin.xmltimetable"
PREFIX = "PPTimetable/"

STORE = "src/data/aws/"

# Ensure directories exist
os.makedirs(STORE, exist_ok=True)

# Create S3 client
s3 = boto3.client(
    's3',
    region_name='eu-west-1',
    aws_access_key_id=AWS_ACCESS,
    aws_secret_access_key=AWS_SECRET
)

def download_file(bucket, key, download_path):
    """Download a file from S3 bucket to local path."""
    
    s3.download_file(bucket, key, download_path)
    
    print(f"Downloaded {key} to {download_path}")
    
    if not download_path.endswith(".gz"):
        return
    
    selected_store_path = os.path.join(STORE, os.path.basename(download_path)[:-3])
    
    with gzip.open(download_path, 'rb') as f_in:
        with open(selected_store_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    print(f"Extracted GZ to {selected_store_path}")
    os.remove(download_path)
    print(f"Deleted {download_path}")

def retrieve_files_from_s3():
    """Retrieve the latest ref and timetable files from S3 bucket."""

    for filename in os.listdir(STORE):
        file_path = os.path.join(STORE, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"Deleted {file_path}")

    # List files in bucket
    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=PREFIX)

    if 'Contents' not in response:
        print("No files found.")
        return

    ref_files = []
    route_files = []

    # Separate ref and route files
    for obj in response['Contents']:
        key = obj['Key']
        if key.endswith('.xml.gz'):
            if 'ref' in key.lower():
                ref_files.append(obj)
            else:
                route_files.append(obj)

    # Sort by LastModified
    ref_files.sort(key=lambda x: x['LastModified'], reverse=True)
    route_files.sort(key=lambda x: x['LastModified'], reverse=True)

    # Download the latest files
    if ref_files:
        ref_key = ref_files[0]['Key']
        ref_path = os.path.join(STORE, os.path.basename(ref_key))
        download_file(BUCKET_NAME, ref_key, ref_path)

    if route_files:
        route_key = route_files[0]['Key']
        route_path = os.path.join(STORE, os.path.basename(route_key))
        download_file(BUCKET_NAME, route_key, route_path)

if __name__ == "__main__":
    retrieve_files_from_s3()