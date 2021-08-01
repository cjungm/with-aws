#!/bin/bash

aws s3 cp s3://cjm-oregon/champion/emr/step_script/transform_python.py /home/hadoop/transform_python.py
sudo rm -r /usr/local/lib64/python3.7/site-packages/numpy*
sudo pip3 install numpy pandas pyhive thrift sasl thrift_sasl --use-feature=2020-resolver --ignore-installed
