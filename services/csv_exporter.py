import csv
from pathlib import Path
from typing import List
from datetime import datetime

from models.metrics import HealthMetrics


def export_metrics_to_csv(metrics_list: List[HealthMetrics], filepath: str) -> None:
    """Export metrics to CSV file for analysis."""
    if not metrics_list:
        return

    # Ensure directory exists
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        'timestamp',
        'node_name',
        'block_height',
        'current_block_height',
        'peers_count',
        'finality_lag',
        'time_since_last_block',
        'rpc_response_time',
        'status'
    ]

    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for metric in metrics_list:
            row = {
                'timestamp': metric.timestamp.isoformat(),
                'node_name': metric.node_name,
                'block_height': metric.block_height,
                'current_block_height': metric.current_block_height,
                'peers_count': metric.peers_count,
                'finality_lag': metric.finality_lag,
                'time_since_last_block': metric.time_since_last_block,
                'rpc_response_time': metric.rpc_response_time,
                'status': metric.status,
            }
            writer.writerow(row)


def load_metrics_from_csv(filepath: str) -> List[HealthMetrics]:
    """Load metrics from CSV file and parse back to HealthMetrics objects."""
    metrics_list = []

    if not Path(filepath).exists():
        return metrics_list

    with open(filepath, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            metric = HealthMetrics(
                timestamp=datetime.fromisoformat(row['timestamp']),
                node_name=row['node_name'],
                block_height=int(row['block_height']),
                current_block_height=int(row['current_block_height']),
                peers_count=int(row['peers_count']),
                finality_lag=int(row['finality_lag']),
                time_since_last_block=int(row['time_since_last_block']),
                rpc_response_time=float(row['rpc_response_time']),
                status=row['status'],
            )
            metrics_list.append(metric)

    return metrics_list
