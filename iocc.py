import argparse
import configparser
import os
import datetime
import uddr_client
import time
import json
from multiprocessing import Pool
from joblib import Parallel, delayed
import csv

# Step 1: Parsing configuration from .ini file
config = configparser.ConfigParser()
config.read('config.ini')
client_id = config['UltraDDR']['ClientID']

# Step 2: Define the date format for our CSV output
generationdate = datetime.datetime.now().strftime("%Y.%m.%d %I:%M:%S %p")
today = datetime.datetime.now().strftime("%Y-%m-%d")

# Step 3: Define our IOC class. This will hold information about each IOC.
class IOC:
    def __init__(self, name):
        self.name = name
        self.status = ''

    # Get the UltraDDR status for this IOC.
    def get_status(self):
        # Attempt to query the IOC
        c = uddr_client.connect(client_id=client_id)
        ddr_results = None
        try:
            ddr_results = c.doh(self.name)
            # Process the results
            ddr_status = ddr_results.status()
            q_type = json.loads(str(ddr_results))['Question'][0]['type']
            if q_type == 12:
                self.status = 'PTR'
            elif ddr_status['rcode'] == 0:
                if 'is blocked by UDDR' in ddr_results.block_info():
                    self.status = 'Blocked'
                else:
                    self.status = 'Not Blocked'
            else:
                self.status = ddr_status['message']
        except Exception as e:
            print(f"Error looking up {self.name}: {e}")
            if not ddr_results:
                self.status = "Lookup Error"

# Step 4: Process a single IOC.
# This will create an IOC object, get its status, and return a dictionary with the results.
def process_ioc(name):
    ioc = IOC(name)
    ioc.get_status()
    return {'name': ioc.name, 'status': ioc.status}

# Step 5: Process a list of IOCs in parallel.
def process_iocs_parallel(ioc_names):
    with Pool(processes=5) as pool:
        return pool.map(process_ioc, ioc_names)

# Step 6: Function to write the results to a CSV file.
def write_csv(results, filename):
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'status'])
        writer.writeheader()
        writer.writerows(results)

# Step 7: Main function.
# This will parse command-line arguments, read the list of IOCs from a file, process them, and write the results to a CSV file.
def main():
    parser = argparse.ArgumentParser(description='Send queries for IOC to UltraDDR.')
    parser.add_argument('-i', '--input', required=True, help='Input file with one IOC per line.')
    parser.add_argument('-o', '--output', required=True, help='Output CSV file.')
    args = parser.parse_args()

    # Read the list of IOCs from the input file.
    ioc_names = []
    with open(args.input, 'r') as f:
        for line in f:
            stripped_line = line.strip()
            if not stripped_line:
                print(f"Skipping blank line.")
                continue
            elif stripped_line.startswith('#'):
                print(f"Skipping commented line: {stripped_line}")
                continue
            else:
                ioc_names.append(stripped_line)

    # Process the IOCs in parallel.
    results = process_iocs_parallel(ioc_names)

    # Write the results to the output CSV file.
    write_csv(results, args.output)

if __name__ == '__main__':
    main()