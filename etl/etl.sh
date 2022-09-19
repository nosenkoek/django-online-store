#!/bin/bash

checked_status_server() {
  result=false

  for (( i=1; i <= 5; i++ ))
  do
    status=$(curl -s -o /dev/null -w "%{http_code}" http://es:9200/)
    if [ $status -eq 200 ]
    then
      result=true
      break
    fi
    sleep 5
    echo 'restart ping'
  done

  return $result
}

echo 'script bash run'
sleep 20
result=checked_status_server

if [ ! $result ]
then
  echo 'ERROR not connection for es'
  exit
fi

python init.py
echo 'init done'

while true
do
  result=checked_status_server
  if [ ! $result ]
  then
    echo 'ERROR not connection for es'
    sleep 5m
    continue
  fi
  python main.py
  echo 'main done'
  sleep 5m
done
