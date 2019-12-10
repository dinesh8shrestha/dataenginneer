import json
import datetime
import time

import pandas as pd

from airflow import DAG
from airflow.operators.bash_operator import BashOperator 
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

from clickhouse_driver import Client

name_surname = "name_surname"

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2019, 3, 14),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'provide_context': True,
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

dag = DAG(
    name_surname + '_01', 
    default_args=default_args, 
    schedule_interval='0 0 * * *' #every 1h at the beginning?
)

def ch_rt_find_latest_full_hour(**kwargs):

  #current time
  now = time.time()

  #prev hour
  prev_hour = now - 3600

  #get from hooks
  table_name_rt = name_surname + "_lab01_rt"

  client = Client(host='localhost', port=9090)

  #get latest timestamp from the rt table.
  query = "select toUnixTimestamp(max(timestamp)) from {}".format(table_name_rt)
  res = client.execute(query)
  print(res)

  #align to whole hours.
  latest_t = res[0][0]
  latest_h = latest_t - (latest_t % 3600)

  return latest_h

def ch_agg_hourly_aggregate_before_latest_hour(**kwargs):
  ti = kwargs['ti']
  td = kwargs['templates_dict']

  #get from hooks
  table_name_agg = name_surname + "_lab01_agg_hourly"
  table_name_rt  = name_surname + "_lab01_rt"

  #get from xcom (as saved by find_files
  latest_h = ti.xcom_pull(key=None, task_ids='find_latest_h')
  print("LATEST_H", latest_h)

  #instantiate CH client
  client = Client(host='localhost', port=9090)

  #read everything to aggregate
  columns = ['eventType','item_price','partyId','sessionId','timestamp']

  query = """select {} 
             from {} 
             where timestamp < {} and isDeleted=0
                   and detectedDuplicate=0 and detectedCorruption=0
          """.format(",".join(columns),table_name_rt, latest_h)

  res = client.execute(query)
  print(len(res))

  #nothing to do?
  if (len(res)<1):
     return
  
  print(res[0])

  #import into pandas dataframe
  df = pd.DataFrame(res, columns=columns)
  print(df.head())

  #For aggregation with ItemBuyEvent

  df_buy = df[df["eventType"] == "itemBuyEvent"].set_index("timestamp").resample("60 min").agg(
    {
        "item_price": 'sum', 
        "partyId": 'nunique',
        "sessionId": 'nunique'
    }
  ).rename(columns={"item_price":"revenue", "sessionId": 'purchases', "partyId":'buyers'})

  df_buy['revenue'] = df_buy['revenue'].astype('float')

  print(df_buy)

  # For all events - visitors

  s_all = df.set_index("timestamp").resample("60 min")['partyId'].nunique().rename("visitors")

  print(s_all)

  # join them
  df_all = df_buy.join(s_all)
  print(df_all)

  # add cr and aov
  df_all = df_all.assign(cr=df_all['buyers']/df_all['visitors'])\
                 .assign(aov=df_all['revenue']/df_all['purchases'])\
                 .fillna(0)
  print(df_all)

  #back to time column instead of time index
  df_flat = df_all.reset_index().rename(columns={'timestamp':'ts_start'})
#  df_flat
#  df_flat['ts_start'] = df_flat['ts_start'].astype('datetime64[s]')
  df_flat = df_flat.assign(ts_end=df_flat['ts_start']+ pd.Timedelta(hours=1))

  print(df_flat)
#  df_flat['ts_end']=df_flat.loc[-2, 'ts_end'] + pd.Timedelta(hours=1)
#  print(df_flat.interpolate(method='time'))
#  print(df_flat)

  #insert into agg_hourly table
  values = json.loads(df_flat.to_json(lines=False, orient='records'))

  #convert ms to s
  for val in values:
    val['ts_start'] //= 1000
    val['ts_end']   //= 1000

  #
  # Insert into agg_hourly
  # 
  print(json.dumps(values, indent=4))
  query = "INSERT INTO {} VALUES".format(table_name_agg)
  res = client.execute(query, values)

  #
  # Update rt : mark isDeleted=1 for these values
  #
  query = "ALTER TABLE {} UPDATE isDeleted = 1 WHERE timestamp<{}".format(table_name_rt, latest_h)
  # query = "ALTER TABLE {} DELETE WHERE".format(table_name_rt) 
  client.execute(query)

#
# Define DAG.
#

t1 = PythonOperator(
    task_id='find_latest_h',
    python_callable=ch_rt_find_latest_full_hour,
    provide_context=True,
    templates_dict={'execution_date':'{{ execution_date.strftime("%s") }}'},
    dag=dag
)

t2 = PythonOperator(
    task_id='ch_agg',
    python_callable=ch_agg_hourly_aggregate_before_latest_hour,
    dag=dag
)


t2.set_upstream(t1)


