# Let's Encrypt IPs: Tracking the Evolution of Trusted TLS Certificates for IP Addresses

This repository contains artifacts for the 2026 ISOC Pulse Fellowship project.

The goal was to analyze IP TLS certificates, i.e., those containing IP addresses inside the Subject Alternative Name (SAN) extension of X.509. We specifically focus on certificates issued by certificate authorities (CAs) trusted by Chrome. Self-signed IP certificates are, therefore, out of scope. 

You can download the 2025 dataset of IP TLS certificates here: yevheniya.com/data/isoc_pulse/certificates.json (file size 902.51M).

## Setup

This project was tested on Debian GNU/Linux 12 (16 CPUs / 64GB RAM) with Python 3.11.2.

### Python virtual environment

Create the virtual environment and install the requirements:

```bash
$ python3 -m virtualenv -p python3 .venv
$ source .venv/bin/activate
$ pip3 install -r requirements.txt
```

### System packages

We need Chromium to render some of the figures:

```bash
$ sudo apt update
$ sudo apt install -y chromium
$ export BROWSER_PATH=/usr/bin/chromium
```

## Dataset

Download and store under `data/certificates`:

```bash
$ mkdir data/certificates
$ wget -O data/certificates/certificates.json yevheniya.com/data/isoc_pulse/certificates.json
```

## Descriptive analysis

The `analysis/certs_overview.ipynb` notebook analyses core properties of collected certificates (e.g., issuers, validity, algorithms).

The `analysis/san.ipynb` notebook analyzes IP addresses observed inside the SAN field (e.g., all IPs, unique IPs, distribution per CA).

The `analysis/ips_org.ipynb` notebook analyzes the organizations/countries/RIRs of SAN IPs and their ASNs.

The `analysis/issuance.ipynb` notebook analyzes anomalous issuance patterns and CA changes.

## Deployment signals

The script below queries CaliDog's certstream (`certstream_feed` in format `wss://...`) during `seconds` seconds, extracts unique SAN IPs, and probes the discovered hosts on 24 ports. The results are stored inside `data/deployment`:

```bash
$ ./scripts/active_measurements.sh <seconds> <certstream_feed>
```

Analyze the data in `analysis/deployment.ipynb`.
