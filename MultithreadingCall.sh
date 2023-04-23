#!/bin/bash

for i in {1..10}
do
    #curl "http://192.168.1.103:5003/Project2-ProxyServer.pdf" &
    #curl "http://192.168.1.103:5003/Home.html" &
    curl --output $i".html" "http://192.168.1.103:5003/Home.html" &
    #curl --output $i".pdf" "http://149.125.96.186:8000/sahil.pdf" &
done
