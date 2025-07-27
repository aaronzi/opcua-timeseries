#!/bin/bash
# Script to generate requirements.txt with hashes for better supply chain security

pip-compile --generate-hashes --output-file requirements-hashed.txt requirements.txt
