#!/bin/bash

# test continuously
while true; do inotifywait -r /home/martijn/workspace/grassfire/src -r /home/martijn/workspace/grassfire/test -e modify; nosetests-2.7 --tests=test_grassfire,test_parallel_simple,test_parallel --with-nosenotify --where=/home/martijn/workspace/grassfire/test; done
