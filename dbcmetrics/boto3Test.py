from importlib import resources
import json
import boto3
import os

BUCKET = "sc-tf-remote-state-01"
# TODO: Load stage from (ansible -> env var)
PREFIX = "env:/dev/"
STATEFILE = "terraform.tfstate"

def get_maintenance_windows_from_tfstate(tfstate_path):
    response = s3_client.get_object(Bucket=BUCKET, Key=tfstate_path)
    state = json.loads(response['Body'].read().decode("UTF-8"))
    resources = state['resources']
    cluster_windows=[]
    nodepool_windows=[]
    for res in resources:
        if res.get("type") == "ionoscloud_k8s_cluster":
            cluster_windows.extend(get_maintenance_window_of_module(res))
        elif res.get("type") == "ionoscloud_k8s_node_pool":
            nodepool_windows.extend(get_maintenance_window_of_module(res))
    return (cluster_windows, nodepool_windows)

def get_maintenance_window_of_module(module):
    return module['instances'][0]["attributes"]["maintenance_window"]

# def currently_in_window(window, timespan) -> bool:


session = boto3.session.Session()
s3_client = session.client(
    service_name='s3',
    aws_access_key_id=os.getenv("SC_AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("SC_AWS_SECRET_ACCESS_KEY"),
    endpoint_url='https://s3-eu-central-1.ionoscloud.com',
)
response = s3_client.list_objects(Bucket=BUCKET, Prefix=PREFIX, Delimiter='/')
# TODO: Filter clusters and generate paths 
windows = {}
for subdirectory in response.get("CommonPrefixes"):
    path = subdirectory.get("Prefix")
    cluster_name = path.split("/")[-2]
    tf_path = path + STATEFILE
    cluster_window = get_maintenance_windows_from_tfstate(tf_path)
    # Add only when at least one windows exists
    if cluster_window[0] or cluster_window[1]:
        windows[cluster_name] = cluster_window
        print(f"Saved maintenance windows for {cluster_name}")
print(windows)



# print(cluster_windows,nodepool_windows)


