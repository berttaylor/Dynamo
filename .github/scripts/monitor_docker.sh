#!/bin/bash

docker-compose -f docker-compose.dev.yml up -d
docker-compose -f docker-compose.dev.yml ps
docker-compose -f docker-compose.dev.yml logs

regx='\s*([Rr]unning|[uU]p) \(healthy\)'
secs=90        # Set interval (duration) in seconds.
endTime=$(( $(date +%s) + secs )) # Calculate end time.
while [ $(date +%s) -lt $endTime ]; do  # Loop until interval has elapsed.
    cnt=2
    while IFS= read -r line; do
        if [[ $line =~ $regx ]]; then
            cnt=$((cnt+1))
        fi
    done <<< $(docker-compose -f docker-compose.dev.yml ps)
    echo -en "\rWaiting for services... $cnt/$(docker-compose -f docker-compose.dev.yml ps | wc -l)"
    if [[ $cnt -eq $(docker-compose -f docker-compose.dev.yml ps | wc -l) ]]; then
        echo ""
        exit 0
    fi
    sleep 1
done

docker-compose -f docker-compose.dev.yml ps
docker-compose -f docker-compose.dev.yml logs

exit 1