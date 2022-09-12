#!/bin/bash

echo 'script bash run'

status=$(curl -s -o /dev/null -w "%{http_code}" http://es:9200/)
echo $status

sleep 20

while [ $status -ne 200 ]
do
  sleep 10
  echo 'restart ping'

  status=$(curl -s -o /dev/null -w "%{http_code}" http://es:9200/)
  echo $status
done

python init.py
echo 'init done'

while true
do
  python main.py
  echo 'main done'
  sleep 2m
done