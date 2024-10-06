#!/bin/bash

# Delete contents of specified directories
rm -rf ./chroma_db/* ./textracted/* ./uploads/* ./extracted_images/*

# Run the Python script
python -m src.main