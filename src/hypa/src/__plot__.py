import os
import sys
from ast import literal_eval
from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch

method_labels = ['HPA', 'HyPA', 'MOHA']
colors = ['tab:blue', 'tab:orange', 'tab:green']
groups = ['light', 'medium', 'heavy', 'very heavy']


def create_folder_if_not_existing(path: str, folder_name: str):
    full_path = os.path.join(path, folder_name)

    if not os.path.exists(full_path):
        os.makedirs(full_path)


def boxplots_combined(directory: str):
    plt.rcParams.update({'font.size': 14})

    columns_to_plot = [['latency', 'Latency (s)'],
                       ['cpu_utilization', 'CPU utilization']]

    csv_files = sorted([
        f'{directory}/{file}'
        for file in os.listdir(directory) if file.endswith('.csv')
    ],
                       key=str.lower)

    for col in columns_to_plot:
        _, axs = plt.subplots(1, 1, figsize=(8, 6))

        for idx, file_path in enumerate(csv_files):
            with open(file_path, 'r') as f:
                df = pd.read_csv(file_path,
                                 delimiter=';',
                                 header=None,
                                 names=[
                                     'timestamp', 'cpu_request', 'cpu_limit',
                                     'replicas', 'latency', 'cpu_utilization',
                                     'replica_poll_values'
                                 ])

                values = []

                df[col[0]] = df[col[0]].apply(literal_eval)

                for sublist in df[col[0]]:
                    for value in sublist:
                        if value:
                            values.append(value)

                axs.boxplot(values,
                            positions=[idx + 1],
                            showfliers=True,
                            boxprops=dict(color=colors[idx], linewidth=1.5),
                            medianprops=dict(color="tab:red", linewidth=1.5),
                            widths=0.2)

        axs.set_ylabel(col[1])
        axs.set_xticks(range(1, len(csv_files) + 1))
        axs.set_xticklabels([
            os.path.basename(file_path).split("_")[0]
            for file_path in csv_files
        ],
                            rotation=0)
        axs.set_xlabel('Method')

        plt.grid(True)
        plt.tight_layout()

        plt.savefig(f'{directory}/{col[0].lower().replace(" ", "_")}.png',
                    dpi=400)
        plt.close()


def plot_combined(directory: str):
    plt.rcParams.update({'font.size': 14})

    columns_to_plot = [['cpu_request', 'CPU request (mCPUs)'],
                       ['cpu_limit', 'CPU limit (mCPUs)'],
                       ['replicas', 'Replicas'],
                       ['cpu_utilization', 'CPU utilization'],
                       ['latency', 'Latency (s)']]

    csv_files = sorted([
        f'{directory}/{file}'
        for file in os.listdir(directory) if file.endswith('.csv')
    ],
                       key=str.lower)

    for col in columns_to_plot:
        _, axs = plt.subplots(1, 1, figsize=(8, 6))

        for file_path in csv_files:
            with open(file_path, 'r') as f:
                df = pd.read_csv(file_path,
                                 delimiter=';',
                                 header=None,
                                 names=[
                                     'timestamp', 'cpu_request', 'cpu_limit',
                                     'replicas', 'latency', 'cpu_utilization',
                                     'replica_poll_values'
                                 ])

                df['timestamp'] = df['timestamp'].apply(
                    lambda x: datetime.fromtimestamp(x))

                values = []

                if col[0] == 'latency' or col[0] == 'cpu_utilization':
                    df[col[0]] = df[col[0]].apply(literal_eval)

                    for sublist in df[col[0]]:
                        if sublist:
                            tmp = [value for value in sublist if value]

                            if tmp:
                                values.append(np.mean(tmp))
                            else:
                                values.append(0.0)
                        else:
                            values.append(0.0)
                else:
                    values = df[col[0]]

                axs.plot(df['timestamp'],
                         values,
                         label=os.path.basename(file_path).split("_")[0],
                         linewidth=2.0)

        if col[0] == 'cpu_utilization_values':
            axs.set_ylim([0.0, 1.0])

        axs.xaxis.set_major_locator(mdates.HourLocator(interval=1))
        h_fmt = mdates.DateFormatter('%-H')
        axs.xaxis.set_major_formatter(h_fmt)

        axs.xaxis.set_minor_locator(mdates.HourLocator(interval=1))
        minor_fmt = mdates.DateFormatter('%-H')
        axs.xaxis.set_minor_formatter(minor_fmt)

        axs.set_xlim(min(df['timestamp']), max(df['timestamp']))

        axs.set_ylabel(col[1])
        axs.set_xlabel('Hour of the day')

        legend_patches = [
            Patch(color=colors[i], label=method_labels[i])
            for i in range(len(method_labels))
        ]

        axs.legend(handles=legend_patches,
                   loc='upper left',
                   bbox_to_anchor=(0.1, 1.15),
                   ncol=3)

        plt.grid(True)
        plt.tight_layout()

        plt.savefig(f'{directory}/{col[0].lower().replace(" ", "_")}_raw.png',
                    dpi=400)
        plt.close()


def plot_combined_average(directory: str):
    plt.rcParams.update({'font.size': 14})

    columns_to_plot = [['cpu_request', 'CPU request (mCPUs)'],
                       ['cpu_limit', 'CPU limit (mCPUs)'],
                       ['replicas', 'Replicas'],
                       ['cpu_utilization', 'CPU utilization'],
                       ['latency', 'Latency (s)']]

    csv_files = sorted([
        f'{directory}/{file}'
        for file in os.listdir(directory) if file.endswith('.csv')
    ],
                       key=str.lower)

    for col in columns_to_plot:
        _, axs = plt.subplots(1, 1, figsize=(8, 6))

        for file_path in csv_files:
            with open(file_path, 'r') as f:
                df = pd.read_csv(file_path,
                                 delimiter=';',
                                 header=None,
                                 names=[
                                     'timestamp', 'cpu_request', 'cpu_limit',
                                     'replicas', 'latency', 'cpu_utilization',
                                     'replica_poll_values'
                                 ])

                df['timestamp'] = df['timestamp'].apply(
                    lambda x: datetime.fromtimestamp(x))

                if col[0] == 'cpu_utilization':
                    df[col[0]] = df[col[0]].apply(literal_eval)

                    values = []

                    for sublist in df[col[0]]:
                        if sublist:
                            tmp = [value for value in sublist if value]

                            if tmp:
                                values.append(np.mean(tmp))
                            else:
                                values.append(np.nan)
                        else:
                            values.append(np.nan)

                    data = pd.DataFrame({
                        'timestamp': df['timestamp'],
                        'values': values
                    })
                    hourly_avg = data.resample('h', on='timestamp').mean()

                    axs.plot(hourly_avg.index,
                             hourly_avg['values'],
                             label=os.path.basename(file_path).split("_")[0],
                             linewidth=2.0)
                elif col[0] == 'latency':
                    df[col[0]] = df[col[0]].apply(literal_eval)

                    values = []

                    for sublist in df[col[0]]:
                        if sublist:
                            tmp = [value for value in sublist if value]

                            if tmp:
                                values.append(np.mean(tmp))
                            else:
                                # TODO: append with 0.0 does not make any sense for plot over time, think of something different here
                                values.append(0.0)
                        else:
                            # TODO: append with 0.0 does not make any sense for plot over time, think of something different here
                            values.append(0.0)

                    data = pd.DataFrame({
                        'timestamp': df['timestamp'],
                        'values': values
                    })
                    hourly_avg = data.resample('h', on='timestamp').mean()

                    axs.plot(hourly_avg.index,
                             hourly_avg['values'],
                             label=os.path.basename(file_path).split("_")[0],
                             linewidth=2.0)
                else:
                    data = pd.DataFrame({
                        'timestamp': df['timestamp'],
                        'total_value': df[col[0]]
                    })
                    hourly_avg = data.resample('h', on='timestamp').mean()

                    axs.plot(hourly_avg.index,
                             hourly_avg['total_value'],
                             label=os.path.basename(file_path).split("_")[0],
                             linewidth=2.0)

        if col[0] == 'cpu_utilization_values':
            axs.set_ylim([0.0, 1.0])

        axs.xaxis.set_major_locator(mdates.HourLocator(interval=1))
        h_fmt = mdates.DateFormatter('%-H')
        axs.xaxis.set_major_formatter(h_fmt)

        axs.xaxis.set_minor_locator(mdates.HourLocator(interval=1))
        minor_fmt = mdates.DateFormatter('%-H')
        axs.xaxis.set_minor_formatter(minor_fmt)

        axs.set_xlim(min(df['timestamp']), max(df['timestamp']))

        axs.set_ylabel(col[1])
        axs.set_xlabel('Hour of the day')

        legend_patches = [
            Patch(color=colors[i], label=method_labels[i])
            for i in range(len(method_labels))
        ]

        axs.legend(handles=legend_patches,
                   loc='upper left',
                   bbox_to_anchor=(0.1, 1.15),
                   ncol=3)

        plt.grid(True)
        plt.tight_layout()

        plt.savefig(
            f'{directory}/{col[0].lower().replace(" ", "_")}_raw_avg.png',
            dpi=400)
        plt.close()


def plot_per_scaler(directory: str):
    plt.rcParams.update({'font.size': 14})

    columns_to_plot = [['cpu_request', 'CPU request (mCPUs)'],
                       ['cpu_limit', 'CPU limit (mCPUs)'],
                       ['replicas', 'Replicas'],
                       ['cpu_utilization', 'CPU utilization'],
                       ['latency', 'Latency (s)']]

    csv_files = sorted([
        f'{directory}/{file}'
        for file in os.listdir(directory) if file.endswith('.csv')
    ],
                       key=str.lower)

    for file_path in csv_files:
        with open(file_path, 'r') as f:
            df = pd.read_csv(file_path,
                             delimiter=';',
                             header=None,
                             names=[
                                 'timestamp', 'cpu_request', 'cpu_limit',
                                 'replicas', 'latency', 'cpu_utilization',
                                 'replica_poll_values'
                             ])

            df['timestamp'] = df['timestamp'].apply(
                lambda x: datetime.fromtimestamp(x))
            method = os.path.basename(file_path).split("_")[0].lower()
            create_folder_if_not_existing(directory, method)

        for col in columns_to_plot:
            _, axs = plt.subplots(1, 1, figsize=(8, 6))

            if col[0] == 'latency' or col[0] == 'cpu_utilization':

                df[col[0]] = df[col[0]].apply(literal_eval)

                values = []

                for sublist in df[col[0]]:
                    if sublist:
                        tmp = [value for value in sublist if value]

                        if tmp:
                            values.append(np.mean(tmp))
                        else:
                            values.append(0.0)
                    else:
                        values.append(0.0)

                axs.plot(df['timestamp'],
                         values,
                         label=os.path.basename(file_path).split("_")[0],
                         linewidth=2.0)
            else:
                axs.plot(df['timestamp'],
                         df[col[0]],
                         label=os.path.basename(file_path).split("_")[0],
                         linewidth=2.0)

            if col[0] == 'cpu_utilization_values':
                axs.set_ylim([0.0, 1.0])

            axs.set_ylabel(col[1])
            axs.set_xlabel('Time')
            axs.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

            plt.grid(True)
            plt.tight_layout()
            plt.legend()

            plt.savefig(
                f'{directory}/{method}/{method}_{col[0].lower().replace(" ", "_")}_raw.png',
                dpi=400)
            plt.close()


def plot_calls(directory: str):
    plt.rcParams.update({'font.size': 14})

    csv_files = sorted([
        f'{directory}/{file}'
        for file in os.listdir(directory) if file.endswith('.csv')
    ],
                       key=str.lower)

    total_calls_df = pd.read_csv(f"{directory}working_hours.txt",
                                 delimiter=';',
                                 header=None,
                                 names=['hour', 'calls'])

    total_calls = total_calls_df['calls'].values

    successful_calls_values = []
    method = []

    for file_path in csv_files:
        with open(file_path, 'r') as f:
            df = pd.read_csv(file_path,
                             delimiter=';',
                             header=None,
                             names=[
                                 'timestamp', 'cpu_request', 'cpu_limit',
                                 'replicas', 'latency', 'cpu_utilization',
                                 'replica_poll_values'
                             ])

        method.append(os.path.basename(file_path).split("_")[0])
        df['latency'] = df['latency'].apply(literal_eval)
        latencies = df['latency'].values

        successful_calls: int = 0

        for latency_list in latencies:
            successful_calls += len(latency_list)

        successful_calls_values.append(successful_calls)

    _, axs = plt.subplots(1, 1, figsize=(8, 6))

    for i, successful_calls in enumerate(successful_calls_values):
        rate = successful_calls / sum(total_calls)

        axs.bar(height=rate, x=[i], color=colors[i])
        axs.bar(height=(1.0 - rate), x=[i], color="tab:red", bottom=rate)

    axs.set_xticks([0, 1, 2])
    axs.set_xticklabels(method_labels, rotation=0)

    legend_patches = [
        Patch(color=colors[i], label=method_labels[i])
        for i in range(len(method_labels))
    ]
    legend_patches.append(Patch(color='tab:red', label='Failed'))
    axs.legend(handles=legend_patches,
               loc='upper left',
               bbox_to_anchor=(0.1, 1.15),
               ncol=4)

    axs.set_xlabel('Scaler')
    axs.set_ylabel('Call routing success rate')

    plt.grid(True)
    plt.tight_layout()

    plt.ylabel("Call routing success rate")
    plt.savefig(f'{directory}/call_comparison.png', dpi=400)
    plt.close()


def plot_metrics_grouped(directories: list[str]):
    plt.rcParams.update({'font.size': 14})

    columns_to_plot = [['latency', 'Latency (s)'],
                       ['cpu_utilization', 'CPU utilization']]

    for col in columns_to_plot:
        _, axs = plt.subplots(1, 1, figsize=(8, 6))

        x_position_index = 0

        for directory in directories:
            csv_files = sorted([
                f'{directory}/{file}'
                for file in os.listdir(directory) if file.endswith('.csv')
            ],
                               key=str.lower)

            for idx, file_path in enumerate(csv_files):
                with open(file_path, 'r') as f:
                    df = pd.read_csv(file_path,
                                     delimiter=';',
                                     header=None,
                                     names=[
                                         'timestamp', 'cpu_request',
                                         'cpu_limit', 'replicas', 'latency',
                                         'cpu_utilization',
                                         'replica_poll_values'
                                     ])

                    values = []

                    df[col[0]] = df[col[0]].apply(literal_eval)

                    for sublist in df[col[0]]:
                        for value in sublist:
                            if value:
                                values.append(value)

                axs.boxplot(values,
                            positions=[x_position_index],
                            showfliers=True,
                            boxprops=dict(color=colors[idx], linewidth=1.5),
                            medianprops=dict(color="tab:red", linewidth=1.5),
                            widths=0.5)
                x_position_index += 1
            x_position_index += 1

        axs.set_ylabel(col[1])
        axs.set_xticks([
            np.mean([i + (d * 4) for i in range(len(csv_files))])
            for d in range(len(directories))
        ])
        axs.set_xticklabels(groups, rotation=0)
        axs.set_xlabel('Method')

        legend_patches = [
            Patch(color=colors[i], label=method_labels[i])
            for i in range(len(method_labels))
        ]
        axs.legend(handles=legend_patches, loc='upper left')

        plt.grid(True)
        plt.tight_layout()

        plt.savefig(f'{col[0].lower().replace(" ", "_")}_stacked.png', dpi=400)
        plt.close()


def plot_calls_grouped(directories: list[str]):
    plt.rcParams.update({'font.size': 14})

    successful_call_values = []

    for directory in directories:
        csv_files = sorted([
            f'{directory}/{file}'
            for file in os.listdir(directory) if file.endswith('.csv')
        ],
                           key=str.lower)

        call_values = []

        for file_path in csv_files:
            with open(file_path, 'r') as f:
                df = pd.read_csv(file_path,
                                 delimiter=';',
                                 header=None,
                                 names=[
                                     'timestamp', 'cpu_request', 'cpu_limit',
                                     'replicas', 'latency', 'cpu_utilization',
                                     'replica_poll_values'
                                 ])
                df['latency'] = df['latency'].apply(literal_eval)
                latencies = df['latency'].values

                successful_calls: int = 0

                for latency_list in latencies:
                    successful_calls += len(latency_list)

                call_values.append(successful_calls)
        successful_call_values.append(call_values)

    total_calls = []
    total_values = []

    for directory in directories:
        total_values.append(
            pd.read_csv(f"{directory}working_hours.txt",
                        delimiter=';',
                        header=None,
                        names=['hour', 'calls'])['calls'].tolist())

    for i, eval in enumerate(successful_call_values):
        tmp = []

        for method in eval:
            tmp.append(method / sum(total_values[i]))

        total_calls.append(tmp)

    _, axs = plt.subplots(1, 1, figsize=(8, 6))

    x_position = 0

    for eval in total_calls:
        for jdx, method in enumerate(eval):
            axs.bar(height=method, x=[x_position], color=colors[jdx])
            axs.bar(height=(1.0 - method),
                    x=[x_position],
                    color="tab:red",
                    bottom=method)

            x_position += 1
        x_position += 1

    axs.set_ylabel('Call routing success rate')
    axs.set_xticks([
        np.mean([i + (d * 4) for i in range(len(csv_files))])
        for d in range(len(directories))
    ])
    axs.set_xticklabels(groups, rotation=0)
    axs.set_xlabel('Call volume group')

    legend_patches = [
        Patch(color=colors[i], label=method_labels[i])
        for i in range(len(method_labels))
    ]
    legend_patches.append(Patch(color='tab:red', label='Failed'))
    axs.legend(handles=legend_patches,
               loc='upper left',
               bbox_to_anchor=(0.1, 1.15),
               ncol=4)

    plt.ylim([0.0, 1.0])
    plt.grid(True)
    plt.tight_layout()

    plt.savefig('call_comparison_stacked.png', dpi=400)
    plt.close()


# Run script like this:
#   python3 __plot__.py /small/ /medium/ /large/ /call_center/
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            f'Invalid number of arguments => python3 __plot__.py <folder_1> <folder_2> ...'
        )
        sys.exit(1)

    evaluations = []

    for i in range(1, len(sys.argv)):
        evaluations.append(sys.argv[i])

    # for evaluation in evaluations:
    #     boxplots_combined(directory=evaluation)
    #     plot_combined(directory=evaluation)
    #     plot_combined_average(directory=evaluation)
    #     plot_per_scaler(directory=evaluation)
    #     plot_calls(directory=evaluation)

    plot_metrics_grouped(directories=evaluations)
    plot_calls_grouped(directories=evaluations)
