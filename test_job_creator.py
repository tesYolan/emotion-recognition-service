import subprocess
import sys
import argparse
import time
import yaml


job_addresses = []
for i in range(1):
    p = subprocess.Popen(["snet", "agent", "--at", "0x7fE17B093E13379247336DDD846deF8624Ae8a9C", "create-jobs","--number", "1", "--max-price", "10000000", "--funded", "--signed", "-y"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    contract, err = p.communicate()
    try:
        job_address = yaml.load(contract)['jobs']
        print(job_address[0]['job_address'])
        job_addresses.append(job_address[0]['job_address'])
    except TypeError:
        print("Failed to create a job")

    time.sleep(1)

with open('jobaddresses ' + time.ctime() + '.txt', 'w') as f:
    for job in job_addresses:
        f.write("%s\n" % job)
