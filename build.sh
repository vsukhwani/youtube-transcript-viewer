#!/bin/bash

# Script for Vercel deployment build step
echo "Starting build process..."

# Ensure Python is available
which python || which python3

# Install pip if not found
if ! command -v pip &> /dev/null; then
  echo "Installing pip..."
  curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
  python get-pip.py || python3 get-pip.py
  rm get-pip.py
fi

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt || python -m pip install -r requirements.txt

echo "Build completed!"
