# HyPA - A Hybrid Pod Autoscaler for Enhanced VoIP Performance

This repository contains the Bachelor thesis project by Dominik Gratz and René Hueber, conducted from 2023 to 2024 at the University of Innsbruck, Department of Computer Science, in collaboration with World-Direct.

The project has also been released under the name `ScaleIP: A Hybrid Autoscaling of VoIP Services based on Deep Reinforcement Learning`, with additional contributions from Zahra Najafabadi-Samani, Juan Aznar-Poveda, and Thomas Fahringer from the University of Innsbruck.

HyPA is a hybrid pod autoscaler specifically designed for Cloud VoIP infrastructure operating within containerized orchestration environments like Kubernetes. It provides both horizontal and vertical scaling of VoIP services, ensuring acceptable latency and throughput while optimizing CPU resource usage. Currently, only one service can be scaled at a time. Additionally, this repository includes a SIP call generator using SIPp for training and evaluating models.

The repository also includes the latest three trained models, located in the /src/hypa/models directory. The folders are named according to the corresponding Unix timestamps of the training sessions.

## Requirements

- Python 3.10
- pipenv
- [mysqlclient dependencies](https://github.com/PyMySQL/mysqlclient?tab=readme-ov-file#linux)

If you are using Kubernetes as your container orchestration environment, ensure `kubectl` is also set up!

## Installation

1. Navigate to the directory `src/hypa/`.
2. Run `pipenv shell`.
3. Run `pipenv install -d`.

## Usage

1. Navigate to the folder `src/hypa/`.
2. Use the Makefile for the following tasks:
   - `make train` to train a new model. Ensure that the `TRAIN_ARGS` variable is set with the appropriate parameters beforehand. You may also observe the training process via TensorBoard!
   - `make autoscale` to deploy a trained model, serve its policy, and scale a service. Adjust the `HYPA_ARGS` variable to configure the necessary parameters.
   - `make eval` to evaluate the currently active autoscaling model. Modify the `EVAL_ARGS` variable to fine-tune the evaluation parameters.
   - `make plot` to visualize the evaluation results. Set the `PLOT_ARGS` variable to specify the evaluation folder.
