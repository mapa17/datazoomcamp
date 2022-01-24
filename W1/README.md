# Using Postgress container

```bash
docker run -it \
    -e POSTGRES_USER="root" \
    -e POSTGRES_PASSWORD="root" \
    -e POSTGRES_DB="ny_taxi" \
    -v $(pwd)/postgres/database:/var/lib/postgresql/data \
    -p 5432:5432 \
    postgres:13
```

# Ingest the data

 ```bash
 python data_ingest.py taxi+_zone_lookup.csv taxi_zones
```

```bash
python data_ingest.py yellow_tripdata_2021-01.csv 
```


# Inspect the database

```bash
pgcli -h localhost -p 5432 -u root -d ny_taxi
```

```SQL
DESCRIBE ny_taxi_trips;
```

**Number of trips each day ...**
```
SELECT
     CAST(tpep_pickup_datetime AS DATE) as "day",
     COUNT(1)
 FROM
     ny_taxi_trips t
 GROUP BY
     CAST(tpep_pickup_datetime AS DATE)
 ORDER BY "day" ASC;
```

**Max tip per day ...**
```
SELECT
     CAST(tpep_pickup_datetime AS DATE) as "day", COUNT(1),
     MAX(tip_amount) as max_tip
 FROM
     ny_taxi_trips t
 GROUP BY
     CAST(tpep_pickup_datetime AS DATE)
 ORDER BY "day" ASC;
```

**Most common dropoff location for travels that start in central park**
SELECT
    COUNT(t.index) cnt,
    CONCAT(zdo."Borough", '/', zdo."Zone") AS "dropoff_loc"
FROM
    ny_taxi_trips t LEFT JOIN taxi_zones zpu
        ON t."PULocationID" = zpu."LocationID"
    LEFT JOIN taxi_zones zdo ON t."DOLocationID" = zpu."LocationID"
WHERE t."PULocationID" = 43 AND t
GROUP BY "dropoff_loc"
ORDER BY cnt DESC
LIMIT 100;
