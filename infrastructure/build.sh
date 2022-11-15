#!/bin/bash

req="../requirements.txt"
sed -i '/boto3/d' $req
pip install --target ../webscraping/dependencies -r $req --upgrade
