#!/bin/bash

sudo yum update -y
sudo yum install libevent-devel gcc-c++ cyrus-sasl-devel.x86_64 gcc -y
sudo pip3 install pandas pyhive thrift sasl thrift_sasl