from datetime import datetime
from airflow import DAG
from airflow.operators.bash_operator import BashOperator


dag = DAG(
    "batch_event",
    description="Clickstream events",
    schedule_interval="30 * * * *",
    start_date=datetime(2018, 11, 1),
    catchup=False
)

templated_command = """
cd ~/pipeline
~/.local/bin/pipenv run python event_consumer.py > {{ params.tmp_data_path }}
[ -s {{ params.tmp_data_path }} ] && cat {{ params.tmp_data_path }} | {{ params.insert_cmd }} || echo "No data to insert"
"""

bash_operator = BashOperator(
    task_id="load_events",
    run_as_user='gdd3',
    bash_command=templated_command,
    params={
        "tmp_data_path": "/tmp/events.json",
        "insert_cmd": """clickhouse-client -n --query="SET input_format_skip_unknown_fields=1; INSERT INTO event FORMAT JSONEachRow" """
    },
    dag=dag
)

bash_operator