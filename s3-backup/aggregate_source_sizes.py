#!/usr/bin/env python3
import sys
import json

if len(sys.argv) > 1:
    jsonFile = sys.argv[1]
else:
    jsonFile = '/root/backup_s3/20201102_210900_hidriveinternational_source_sizes.json'
with open(jsonFile) as f:
    data = json.load(f)
    
totalBucketSize = 0
for bucket in data["sizes"]:
    totalBucketSize += bucket["bytes"]
print("Data on drive %s: %s GByte (%s Bytes)" % (data["sourcedrive"], totalBucketSize/(1024*1024*1024), totalBucketSize))
