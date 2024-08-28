#!/bin/bash

# Container settings
uacTc01="uac-tc01"
uacTc02="uac-tc02"
uacTc03="uac-tc03"
uacTc04="uac-tc04"
uacTc05="uac-tc05"
uacTc06="uac-tc06"
uacTc07="uac-tc07"
uacTc08="uac-tc08"
uacTc09="uac-tc09"
uacTc10="uac-tc10"
uacTc11="uac-tc11"
uacTc12="uac-tc12"
uacTc13="uac-tc13"
uacTc14="uac-tc14"
uacTc15="uac-tc15"
uacTc16="uac-tc16"
uacTc17="uac-tc17"
uacTc18="uac-tc18"
uacTc19="uac-tc19"
uacTc20="uac-tc20"
uacTc21="uac-tc21"
uacTc22="uac-tc22"
uacTc23="uac-tc23"
uacTc24="uac-tc24"
uas="uas"

# SIP settings
rasIp=172.25.104.164
rasPort=5060

# Generation settings
totalPhonesPerClient=26
registerTimeout=30
callTimeout=210
secondsPerHour=150
simulateWeekends=false

declare -A busyFactorDictionary=( ["mon"]=20 ["tue"]=20 ["wed"]=12 ["thu"]=12 ["fri"]=8 ["sat"]=0 ["sun"]=0 )


# no arguments
cleanupOldContainers() {
    if [ "$(docker ps -a -q -f name=$uac)" ] || [ "$(docker ps -a -q -f name=$uas)" ]
    then
        echo "Cleanup old containers"
        echo

        docker compose -f docker-compose-train.yml down
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

    startWorker $uacTc01 "/scenarios/phone2ccs_register.xml" "/scenarios/train/train_registrations_tc01.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc02 "/scenarios/phone2ccs_register.xml" "/scenarios/train/train_registrations_tc02.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc03 "/scenarios/phone2ccs_register.xml" "/scenarios/train/train_registrations_tc03.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc04 "/scenarios/phone2ccs_register.xml" "/scenarios/train/train_registrations_tc04.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc05 "/scenarios/phone2ccs_register.xml" "/scenarios/train/train_registrations_tc05.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc06 "/scenarios/phone2ccs_register.xml" "/scenarios/train/train_registrations_tc06.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc07 "/scenarios/phone2ccs_register.xml" "/scenarios/train/train_registrations_tc07.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc08 "/scenarios/phone2ccs_register.xml" "/scenarios/train/train_registrations_tc08.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc09 "/scenarios/phone2ccs_register.xml" "/scenarios/train/train_registrations_tc09.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc10 "/scenarios/phone2ccs_register.xml" "/scenarios/train/train_registrations_tc10.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc11 "/scenarios/phone2ccs_register.xml" "/scenarios/train/train_registrations_tc11.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc12 "/scenarios/phone2ccs_register.xml" "/scenarios/train/train_registrations_tc12.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc13 "/scenarios/phone2ccs_register.xml" "/scenarios/train/train_registrations_tc13.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc14 "/scenarios/phone2ccs_register.xml" "/scenarios/train/train_registrations_tc14.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc15 "/scenarios/phone2ccs_register.xml" "/scenarios/train/train_registrations_tc15.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc16 "/scenarios/phone2ccs_register.xml" "/scenarios/train/train_registrations_tc16.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc17 "/scenarios/phone2ccs_register.xml" "/scenarios/train/train_registrations_tc17.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc18 "/scenarios/phone2ccs_register.xml" "/scenarios/train/train_registrations_tc18.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc19 "/scenarios/phone2ccs_register.xml" "/scenarios/train/train_registrations_tc19.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc20 "/scenarios/phone2ccs_register.xml" "/scenarios/train/train_registrations_tc20.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc21 "/scenarios/phone2ccs_register.xml" "/scenarios/train/train_registrations_tc21.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc22 "/scenarios/phone2ccs_register.xml" "/scenarios/train/train_registrations_tc22.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc23 "/scenarios/phone2ccs_register.xml" "/scenarios/train/train_registrations_tc23.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc24 "/scenarios/phone2ccs_register.xml" "/scenarios/train/train_registrations_tc24.csv" 5 1000 $totalPhonesPerClient $registerTimeout

    echo "Wait for registration to finish..."

    checkWorkerDone $uacTc01
    checkWorkerDone $uacTc02
    checkWorkerDone $uacTc03
    checkWorkerDone $uacTc04
    checkWorkerDone $uacTc05
    checkWorkerDone $uacTc06
    checkWorkerDone $uacTc07
    checkWorkerDone $uacTc08
    checkWorkerDone $uacTc09
    checkWorkerDone $uacTc10
    checkWorkerDone $uacTc11
    checkWorkerDone $uacTc12
    checkWorkerDone $uacTc13
    checkWorkerDone $uacTc14
    checkWorkerDone $uacTc15
    checkWorkerDone $uacTc16
    checkWorkerDone $uacTc17
    checkWorkerDone $uacTc18
    checkWorkerDone $uacTc19
    checkWorkerDone $uacTc20
    checkWorkerDone $uacTc21
    checkWorkerDone $uacTc22
    checkWorkerDone $uacTc23
    checkWorkerDone $uacTc24
    
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

    startWorker $uacTc01 "/scenarios/phone2ccs_unregister.xml" "/scenarios/train/train_registrations_tc01.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc02 "/scenarios/phone2ccs_unregister.xml" "/scenarios/train/train_registrations_tc02.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc03 "/scenarios/phone2ccs_unregister.xml" "/scenarios/train/train_registrations_tc03.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc04 "/scenarios/phone2ccs_unregister.xml" "/scenarios/train/train_registrations_tc04.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc05 "/scenarios/phone2ccs_unregister.xml" "/scenarios/train/train_registrations_tc05.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc06 "/scenarios/phone2ccs_unregister.xml" "/scenarios/train/train_registrations_tc06.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc07 "/scenarios/phone2ccs_unregister.xml" "/scenarios/train/train_registrations_tc07.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc08 "/scenarios/phone2ccs_unregister.xml" "/scenarios/train/train_registrations_tc08.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc09 "/scenarios/phone2ccs_unregister.xml" "/scenarios/train/train_registrations_tc09.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc10 "/scenarios/phone2ccs_unregister.xml" "/scenarios/train/train_registrations_tc10.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc11 "/scenarios/phone2ccs_unregister.xml" "/scenarios/train/train_registrations_tc11.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc12 "/scenarios/phone2ccs_unregister.xml" "/scenarios/train/train_registrations_tc12.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc13 "/scenarios/phone2ccs_unregister.xml" "/scenarios/train/train_registrations_tc13.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc14 "/scenarios/phone2ccs_unregister.xml" "/scenarios/train/train_registrations_tc14.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc15 "/scenarios/phone2ccs_unregister.xml" "/scenarios/train/train_registrations_tc15.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc16 "/scenarios/phone2ccs_unregister.xml" "/scenarios/train/train_registrations_tc16.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc17 "/scenarios/phone2ccs_unregister.xml" "/scenarios/train/train_registrations_tc17.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc18 "/scenarios/phone2ccs_unregister.xml" "/scenarios/train/train_registrations_tc18.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc19 "/scenarios/phone2ccs_unregister.xml" "/scenarios/train/train_registrations_tc19.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc20 "/scenarios/phone2ccs_unregister.xml" "/scenarios/train/train_registrations_tc20.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc21 "/scenarios/phone2ccs_unregister.xml" "/scenarios/train/train_registrations_tc21.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc22 "/scenarios/phone2ccs_unregister.xml" "/scenarios/train/train_registrations_tc22.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc23 "/scenarios/phone2ccs_unregister.xml" "/scenarios/train/train_registrations_tc23.csv" 5 1000 $totalPhonesPerClient $registerTimeout & \
    startWorker $uacTc24 "/scenarios/phone2ccs_unregister.xml" "/scenarios/train/train_registrations_tc24.csv" 5 1000 $totalPhonesPerClient $registerTimeout

    echo "Wait for unregistration to finish..."

    checkWorkerDone $uacTc01
    checkWorkerDone $uacTc02
    checkWorkerDone $uacTc03
    checkWorkerDone $uacTc04
    checkWorkerDone $uacTc05
    checkWorkerDone $uacTc06
    checkWorkerDone $uacTc07
    checkWorkerDone $uacTc08
    checkWorkerDone $uacTc09
    checkWorkerDone $uacTc10
    checkWorkerDone $uacTc11
    checkWorkerDone $uacTc12
    checkWorkerDone $uacTc13
    checkWorkerDone $uacTc14
    checkWorkerDone $uacTc15
    checkWorkerDone $uacTc16
    checkWorkerDone $uacTc17
    checkWorkerDone $uacTc18
    checkWorkerDone $uacTc19
    checkWorkerDone $uacTc20
    checkWorkerDone $uacTc21
    checkWorkerDone $uacTc22
    checkWorkerDone $uacTc23
    checkWorkerDone $uacTc24

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

    startWorker $uacTc01 "/scenarios/phone2ccs_caller.xml" "/scenarios/train/train_calls_tc01.csv" $1 $2 $3 $callTimeout & \
    startWorker $uacTc02 "/scenarios/phone2ccs_caller.xml" "/scenarios/train/train_calls_tc02.csv" $1 $2 $3 $callTimeout & \
    startWorker $uacTc03 "/scenarios/phone2ccs_caller.xml" "/scenarios/train/train_calls_tc03.csv" $1 $2 $3 $callTimeout & \
    startWorker $uacTc04 "/scenarios/phone2ccs_caller.xml" "/scenarios/train/train_calls_tc04.csv" $1 $2 $3 $callTimeout & \
    startWorker $uacTc05 "/scenarios/phone2ccs_caller.xml" "/scenarios/train/train_calls_tc05.csv" $1 $2 $3 $callTimeout & \
    startWorker $uacTc06 "/scenarios/phone2ccs_caller.xml" "/scenarios/train/train_calls_tc06.csv" $1 $2 $3 $callTimeout & \
    startWorker $uacTc07 "/scenarios/phone2ccs_caller.xml" "/scenarios/train/train_calls_tc07.csv" $1 $2 $3 $callTimeout & \
    startWorker $uacTc08 "/scenarios/phone2ccs_caller.xml" "/scenarios/train/train_calls_tc08.csv" $1 $2 $3 $callTimeout & \
    startWorker $uacTc09 "/scenarios/phone2ccs_caller.xml" "/scenarios/train/train_calls_tc09.csv" $1 $2 $3 $callTimeout & \
    startWorker $uacTc10 "/scenarios/phone2ccs_caller.xml" "/scenarios/train/train_calls_tc10.csv" $1 $2 $3 $callTimeout & \
    startWorker $uacTc11 "/scenarios/phone2ccs_caller.xml" "/scenarios/train/train_calls_tc11.csv" $1 $2 $3 $callTimeout & \
    startWorker $uacTc12 "/scenarios/phone2ccs_caller.xml" "/scenarios/train/train_calls_tc12.csv" $1 $2 $3 $callTimeout & \
    startWorker $uacTc13 "/scenarios/phone2ccs_caller.xml" "/scenarios/train/train_calls_tc13.csv" $1 $2 $3 $callTimeout & \
    startWorker $uacTc14 "/scenarios/phone2ccs_caller.xml" "/scenarios/train/train_calls_tc14.csv" $1 $2 $3 $callTimeout & \
    startWorker $uacTc15 "/scenarios/phone2ccs_caller.xml" "/scenarios/train/train_calls_tc15.csv" $1 $2 $3 $callTimeout & \
    startWorker $uacTc16 "/scenarios/phone2ccs_caller.xml" "/scenarios/train/train_calls_tc16.csv" $1 $2 $3 $callTimeout & \
    startWorker $uacTc17 "/scenarios/phone2ccs_caller.xml" "/scenarios/train/train_calls_tc17.csv" $1 $2 $3 $callTimeout & \
    startWorker $uacTc18 "/scenarios/phone2ccs_caller.xml" "/scenarios/train/train_calls_tc18.csv" $1 $2 $3 $callTimeout & \
    startWorker $uacTc19 "/scenarios/phone2ccs_caller.xml" "/scenarios/train/train_calls_tc19.csv" $1 $2 $3 $callTimeout & \
    startWorker $uacTc20 "/scenarios/phone2ccs_caller.xml" "/scenarios/train/train_calls_tc20.csv" $1 $2 $3 $callTimeout & \
    startWorker $uacTc21 "/scenarios/phone2ccs_caller.xml" "/scenarios/train/train_calls_tc21.csv" $1 $2 $3 $callTimeout & \
    startWorker $uacTc22 "/scenarios/phone2ccs_caller.xml" "/scenarios/train/train_calls_tc22.csv" $1 $2 $3 $callTimeout & \
    startWorker $uacTc23 "/scenarios/phone2ccs_caller.xml" "/scenarios/train/train_calls_tc23.csv" $1 $2 $3 $callTimeout & \
    startWorker $uacTc24 "/scenarios/phone2ccs_caller.xml" "/scenarios/train/train_calls_tc24.csv" $1 $2 $3 $callTimeout

    echo "Wait for calls to finish..."

    checkWorkerDone $uacTc01
    checkWorkerDone $uacTc02
    checkWorkerDone $uacTc03
    checkWorkerDone $uacTc04
    checkWorkerDone $uacTc05
    checkWorkerDone $uacTc06
    checkWorkerDone $uacTc07
    checkWorkerDone $uacTc08
    checkWorkerDone $uacTc09
    checkWorkerDone $uacTc10
    checkWorkerDone $uacTc11
    checkWorkerDone $uacTc12
    checkWorkerDone $uacTc13
    checkWorkerDone $uacTc14
    checkWorkerDone $uacTc15
    checkWorkerDone $uacTc16
    checkWorkerDone $uacTc17
    checkWorkerDone $uacTc18
    checkWorkerDone $uacTc19
    checkWorkerDone $uacTc20
    checkWorkerDone $uacTc21
    checkWorkerDone $uacTc22
    checkWorkerDone $uacTc23
    checkWorkerDone $uacTc24

    echo "Worker finished!"
    echo

    sleep 30

    stopWorker $uas
    checkWorkerDone $uas

    echo "Calls finished"
    echo
}



echo "RL TRAINING CALLS"
echo

cleanupOldContainers

echo "Start docker containers..."
echo

docker compose -f docker-compose-train.yml up -d 

echo "Start calls..."
echo


echo "Start calls..."
echo "1 hour simulated as $secondsPerHour seconds"
echo

currentDay=0

while true
do 
    echo "Register phones..."
    echo

    registerPhones

    if $simulateWeekends
    then
        ((currentDay=$currentDay % 7))
    else
        ((currentDay=$currentDay % 5))
    fi

    case $currentDay in
        0)
            echo "Current day is: Monday"
            busyFactor="${busyFactorDictionary["mon"]}"
            ;;

        1)
            echo "Current day is: Tuesday"
            busyFactor="${busyFactorDictionary["tue"]}"
            ;;

        2)
            echo "Current day is: Wednesday"
            busyFactor="${busyFactorDictionary["wed"]}"
            ;;

        3)
            echo "Current day is: Thuesday"
            busyFactor="${busyFactorDictionary["thu"]}"
            ;;

        4)
            echo "Current day is: Friday"
            busyFactor="${busyFactorDictionary["fri"]}"
            ;;

        5)
            echo "Current day is: Saturday"
            busyFactor="${busyFactorDictionary["sat"]}"
            ;;

        6)
            echo "Current day is: Sunday"
            busyFactor="${busyFactorDictionary["sun"]}"
            ;;
    esac

    echo "Busy factor for this day: $busyFactor"
    echo

    for hour in {0..23}
    do
        echo
        echo "Current hour: $hour"

        callsPerHour=$( awk -F ';' -v pat="^$hour$" '$1 ~ pat { print $2 }' average_calls_per_hour.csv )
        callsPerHour=${callsPerHour//$'\r'/}

        if [ $simulateWeekends ] || [ "$callsPerHour" = "0" ]
        then
            factor=0
        else
            factor=$(( 0 + $RANDOM % $busyFactor ))
        fi

        echo "Busy value: $factor"

        callsPerHour=$(( $callsPerHour + $factor ))

        echo "Number of calls for this hour: $callsPerHour"

        if [ "$callsPerHour" = "0" ]
        then
            sleep $secondsPerHour
            continue
        fi

        stepSize=$(( ($secondsPerHour * 1000) / $callsPerHour ))

        echo "Step size: $stepSize ms"

        startCalls 1 $stepSize $callsPerHour

        echo "Finished hour: $hour"
    done

    ((currentDay++))

    echo "Finished day: $currentDay"
    echo
done
