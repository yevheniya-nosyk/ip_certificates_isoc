#!/bin/bash

# The root directory of this repository
repo_dir=$(git rev-parse --show-toplevel)
# Load the virtual environment
source $repo_dir/.venv/bin/activate

# How long to run the certstream for
seconds=$1
certstream=$2

# Create the working directory
work_dir=$repo_dir/data/deployment
mkdir -p $work_dir/{certstream,probing}

# Get the timestamp for the file name
now=$(date '+%Y-%m-%d-%H-%M-%S')

# Analyze the certstream during X seconds
timeout $seconds python3 $repo_dir/src/get_certstream.py -w $work_dir/certstream -c $certstream > $work_dir/certstream/$now.json

# # Do the active collection of certificates
# python3 $repo_dir/src/get_certificates.py -w $work_dir/probing -c $work_dir/certstream/$now.json > $work_dir/probing/$now.json
