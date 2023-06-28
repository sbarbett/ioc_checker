ioc_checker
======================

This utility serves the same function as [ultraddr-ioc-checker](https://github.com/rybolov/UltraDDR-IOC-Checker/tree/master), but it handles the DoH requests using [uddr_client](https://github.com/sbarbett/uddr_client).

The tool iterates through the IOCs in a text file (these lists of compromised entities come from various threat intelligence sources) and query them against the UDDR resolvers. New domains will automatically be seeded in to the Watch Engine and potentially blocked.

Similarly to the original tool, this will scrape relevant DNS parts from urls (obfuscated or not) and emails. For IPv4 and IPv6 addresses, it will format them appropriately and do a reverse DNS lookup. This is all handled natively by the client.

## IoC Status

The output will contain statuses as follows:

1. Blocked: The DNS resolved to the UDDR blocked page
2. Not Blocked: Resolved, but wasn't blocked
3. PTR: IP addresses will be PTR queries
4, Anything else that returns a status that isn't '0' (NOERR) will give the status message (NXDOMAIN, SERVFAIL, etc.)

## Setup

You will want to copy the config.ini.example file to config.ini and add your client ID. Install the uddr_client dependency, which is in the requirements.txt file.

```bash
pip3 install -r requirements.txt
```

Then simply run:

```bash
python3 iocc.py -i inputfile.txt -o outputfile.csv
```

I borrowed the testfile.txt from ultraddr-ioc-checker and put it in the data folder.