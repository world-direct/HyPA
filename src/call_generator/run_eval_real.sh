#!/bin/bash

# Container settings
uacHpa="uac_hpa"
uacHypa="uac_hypa"
uacMoha="uac_moha"
uas="uas"

# SIP settings
rasIp=172.25.104.164
rasPort=5060

# Generation settings
totalPhonesPerClient=26
registerTimeout=30
callTimeout=3660
secondsPerHour=3600


# no arguments
cleanupOldContainers() {
    if [ "$(docker ps -a -q -f name=$uac)" ] || [ "$(docker ps -a -q -f name=$uas)" ]
    then
        echo "Cleanup old containers"
        echo

        docker compose -f docker-compose-eval.yml down
    fi
}

# arguments:
# - $1: container
checkWorkerDone() {
    while :
    do
        if docker exec $1 ps -ea | grep -q sipp
        then
            sleep 10
        else
            echo "Worker $1 is done"
            break
        fi
    done
}

# arguments:
# - $1: container name
# - $2: scenario
# - $3: injection file
# - $4: call rate in calls per second (r)
# - $5: rate period (rp)
# - $6: total calls (m)
# - $7: timeout
startWorker() {
    echo "Start worker with params: $1, $2, $3, $4, $5, $6, $7"

    docker exec -d -it $1 sipp $rasIp:$rasPort -p 5060 \
            -sf $2 \
            -inf $3 \
            -r $4 \
            -rp $5 \
            -m $6 \
            -trace_msg \
            -timeout $7 \
            -pause_msg_ign \
            -timeout_error \
            -trace_err \
            -message_file test/testing.log \
            -error_file test/error.log > /dev/null

    sleep 1
}

# arguments:
# - $1: container
stopWorker() {
    echo "Stop worker $1..."
    echo

    docker exec -d -it $1 pkill sipp

    echo "Done"
}

# no arguments
registerPhones() {
    echo "Start REFER listener on container $uas"
    echo

    docker exec -d -it $uas sipp $rasIp:$rasPort -p 5060 \
        -sf /scenarios/ccs2phone_refer.xml \
        -trace_msg \
        -pause_msg_ign \
        -timeout_error \
        -trace_err \
        -message_file test/testing.log \
        -error_file test/error.log > /dev/null
    
    sleep 1

    echo "Run phone registrations"
    echo

    startWorker $uacHpa "/scenarios/phone2ccs_register.xml" "/scenarios/evaluation/eval_registrations_hpa.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacHypa "/scenarios/phone2ccs_register.xml" "/scenarios/evaluation/eval_registrations_hypa.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacMoha "/scenarios/phone2ccs_register.xml" "/scenarios/evaluation/eval_registrations_moha.csv" 5 1000 $totalPhonesPerClient $registerTimeout

    echo "Wait for registration to finish..."

    checkWorkerDone $uacHpa
    checkWorkerDone $uacHypa
    checkWorkerDone $uacMoha
    
    echo "Registration workers finished!"
    echo

    sleep 10

    stopWorker $uas
    checkWorkerDone $uas

    echo "Registration finished"
    echo
}

# no arguments
unregisterPhones() {
    echo "Run phone unregistration"
    echo

    startWorker $uacHpa "/scenarios/phone2ccs_unregister.xml" "/scenarios/evaluation/eval_registrations_hpa.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacHypa "/scenarios/phone2ccs_unregister.xml" "/scenarios/evaluation/eval_registrations_hypa.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacMoha "/scenarios/phone2ccs_unregister.xml" "/scenarios/evaluation/eval_registrations_moha.csv" 5 1000 $totalPhonesPerClient $registerTimeout

    echo "Wait for unregistration to finish..."

    checkWorkerDone $uacHpa
    checkWorkerDone $uacHypa
    checkWorkerDone $uacMoha

    echo "Unregistration finished"
    echo
}

# arguments:
# - $1: call rate in calls per second (r)
# - $2: rate period (rp)
# - $3: total calls (m)
startCalls() {
    echo "Start callee handler"
    echo "CR/s: $1, rp: $2, tc: $3"
    echo

    docker exec -d -it $uas sipp $rasIp:$rasPort -p 5060 \
        -sf /scenarios/phone2ccs_called.xml \
        -trace_msg \
        -pause_msg_ign \
        -timeout_error \
        -trace_err \
        -message_file test/testing.log \
        -error_file test/error.log > /dev/null

    sleep 1

    echo "Start call generator"
    echo

    startWorker $uacHpa "/scenarios/phone2ccs_caller.xml" "/scenarios/evaluation/eval_calls_hpa.csv" $1 $2 $3 $callTimeout & \
    startWorker $uacHypa "/scenarios/phone2ccs_caller.xml" "/scenarios/evaluation/eval_calls_hypa.csv" $1 $2 $3 $callTimeout & \
    startWorker $uacMoha "/scenarios/phone2ccs_caller.xml" "/scenarios/evaluation/eval_calls_moha.csv" $1 $2 $3 $callTimeout

    echo "Wait for calls to finish..."

    checkWorkerDone $uacHpa
    checkWorkerDone $uacHypa
    checkWorkerDone $uacMoha

    echo "Worker finished!"
    echo

    sleep 30

    stopWorker $uas
    checkWorkerDone $uas

    echo "Calls finished"
    echo
}



echo "REAL WORLD EVALUATION"
echo

cleanupOldContainers

echo "Start docker containers..."
echo

docker compose -f docker-compose-eval.yml up -d 

echo "Start calls..."
echo


for hour in {7..17}
do
    echo "Register phones..."
    echo
    
    registerPhones

    echo
    echo "Current hour: $hour"

    callsPerHour=$( awk -F ';' -v pat="^$hour$" '$1 ~ pat { print $2 }' working_hours_real.csv )
    callsPerHour=${callsPerHour//$'\r'/}

    echo "Number of calls for this hour: $callsPerHour"

    stepSize=$(( ($secondsPerHour * 1000) / $callsPerHour ))

    echo "Step size: $stepSize ms"

    startCalls 1 $stepSize $callsPerHour

    echo "Finished hour: $hour"
done


sleep 5

echo "Unregister phones..."
echo

unregisterPhones

echo "Cleanup containers"
echo

docker compose -f docker-compose-eval.yml down

echo "Finished!"
