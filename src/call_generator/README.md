# Call Generator

A simple SIP call generator designed to create internal SIP calls for multiple tenants simultaneously. This generator allows you to schedule a specific number of calls per hour based on a provided CSV file. In the CSV, the first column represents the hour of the day, and the second column specifies the number of calls to generate during that hour.

To introduce variability in the call patterns, a `busy factor` is randomly applied, with higher activity at the beginning of the week (Monday) and gradually decreasing towards the end of the week. The `secondsPerHour` parameter lets you compress the duration of an hour, allowing you to simulate an entire day in just a few minutes.

## Overview

This project leverages two SIPp Docker services, to generate and manage calls:

- **`uac`**: Registers phones and initiates calls. For each tenant one `uac` container exists.
- **`uas`**: Handles SIP REFERs and answers calls for all tenants.

Initially, both containers remain idle, waiting for a SIPp process to start. This process is triggered by the `run_train.sh` or `run_eval_real.sh` script, which simulates weekly call behavior by compressing one hour of activity into the value of variable `secondsPerHour`.

## Getting Started

To start the call generator, simply execute the `run_train.sh` or `run_eval_real.sh` script. It is recommended to run the script within a `tmux` session to prevent it from stopping if the SSH connection is closed.

### Configurable Variables

Below are the configurable variables available in the `run_train.sh` or `run_eval_real.sh` script:

```sh
# SIP settings
rasIp=172.25.104.164            # RAS IP address
rasPort=5060                    # RAS SIP port
totalPhonesPerClient=26         # Total number of phones used for call generation
registerTimeout=30              # Registration timeout in seconds
callTimeout=210                 # SIP Call timeout in seconds

# Generation settings
secondsPerHour=150              # Real-time seconds representing one simulated hour
simulateWeekends=false          # If set to `false`, only simulate calls from Monday to Friday
```

## Building the Docker Image

To build the Docker image for the SIPp services, run the following command:

```sh
docker build --pull --rm -f "src/call_generator/Dockerfile" -t sipp:3.7.2 "src/call_generator"
```

## Testing

### Registration

To test the registration process, use the following SIPp commands:

* UAS (Server):

```sh
sipp 172.25.104.164:5060 -p 5061 \
        -sf /scenarios/ccs2phone_refer.xml \
        -trace_msg \
        -pause_msg_ign \
        -timeout_error \
        -trace_err \
        -message_file test/testing.log \
        -error_file test/error.log > /dev/null
```

* UAC (Client):

```sh
# uac
sipp 172.25.104.164:5060 -p 5060 \
        -sf /scenarios/phone2ccs_register.xml \
        -inf /scenarios/test_registrations.csv \
        -r 4 \
        -rp 1000 \
        -m 26 \
        -trace_msg \
        -timeout 90 \
        -pause_msg_ign \
        -timeout_error \
        -trace_err \
        -message_file test/testing.log \
        -error_file test/error.log > /dev/null
```

* UAC (Interactive Mode):

```sh
sipp 172.25.104.164:5060 -p 5060 -sf /scenarios/phone2ccs_register.xml -inf /scenarios/test_registrations.csv
```

### Call Simulation

To simulate calls, use the following SIPp commands:

* UAS (Server):

```sh
sipp 172.25.104.164:5060 -p 5061 \
        -sf /scenarios/phone2ccs_called.xml \
        -trace_msg \
        -pause_msg_ign \
        -timeout_error \
        -trace_err \
        -message_file test/testing.log \
        -error_file test/error.log > /dev/null
```

* UAC (Client):

```sh
# uac
sipp 172.25.104.164:5060 -p 5060 \
        -sf /scenarios/phone2ccs_caller.xml \
        -inf /scenarios/test_calls.csv \
        -r 1 \
        -rp 5000 \
        -m 10 \
        -trace_msg \
        -pause_msg_ign \
        -timeout_error \
        -trace_err \
        -message_file test/testing.log \
        -error_file test/error.log > /dev/null
```

* UAC (Interactive Mode):

```sh
sipp 172.25.104.164:5060 -p 5060 -sf /scenarios/phone2ccs_caller.xml -inf /scenarios/test_calls.csv
```
