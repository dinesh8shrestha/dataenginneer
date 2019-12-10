 view в click house

```
login=name_surname
cat << END | clickhouse-client --port 9090 --multiline
create view ${login}_lab03_view as 
select 
SUM(revenue) as revenue, 
SUM(purchases) as purchases,
revenue/purchases as aov
from(
  select 
  CAST(SUM(revenue) as Float32) as revenue, 
  CAST(COUNT(DISTINCT sessionId) as Integer) as purchases 
  from (
    select
    timestamp,
    case when detectedDuplicate=0 and detectedCorruption=0 and eventType == 'itemBuyEvent' then item_price else null end as revenue,
    case when detectedDuplicate=0 and detectedCorruption=0 and eventType = 'itemBuyEvent' then sessionId else null end as sessionId
    from
    ${login}_lab01_rt
    where isDeleted=0
  )
  
  UNION ALL

  select SUM(revenue) as revenue, SUM(purchases) as purchases
  from
  ${login}_lab01_agg_hourly
)
END
```

python ./service.py

```
python ./lab03_flask.py
```