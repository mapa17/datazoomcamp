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

## Number of trips each day
```SQL
SELECT
     CAST(tpep_pickup_datetime AS DATE) as "day",
     COUNT(1)
 FROM
     ny_taxi_trips t
 GROUP BY
     CAST(tpep_pickup_datetime AS DATE)
 ORDER BY "day" ASC;
```

## Max tip per day
```SQL
SELECT
     CAST(tpep_pickup_datetime AS DATE) as "day", COUNT(1),
     MAX(tip_amount) as max_tip
 FROM
     ny_taxi_trips t
 GROUP BY
     CAST(tpep_pickup_datetime AS DATE)
 ORDER BY "day" ASC;
```

**Improvements**
One can do the GROUP BY on results form SELECT instead of casting again

## Most common dropoff location for travels that start in central park
```SQL
SELECT
    COUNT(t.index) cnt,
    CONCAT(zdo."Borough", '/', zdo."Zone") AS "dropoff_loc"
FROM
    ny_taxi_trips t
LEFT JOIN taxi_zones zpu
    ON t."PULocationID" = zpu."LocationID"
LEFT JOIN taxi_zones zdo
    ON t."DOLocationID" = zpo."LocationID"
WHERE t."PULocationID" = 43
GROUP BY "dropoff_loc"
ORDER BY cnt DESC
LIMIT 100;
```

**Improvements**
One can use the SQL function `COALESCE()` in order to return none empty values from a list (have a default value) see [here](https://www.w3schools.com/sql/func_sqlserver_coalesce.asp)

So if there is no value in a selection or column 'Unknown' will be used instead
```SQl
    CONCAT(COALESCE(zdo."Borough", 'Unknown'), '/', COALESCE(zdo."Zone", 'Unknown')) AS "dropoff_loc"
```

In addition instead of filtering for a constant (43) one can use pattern matching with `ILIKE`
Where `%` can stand for one or more characters.

```SQL
WHERE t."PULocationID" ILIKE '%central park%' 
```

## Number of different drop off locations from central park
```SQL
SELECT
    CAST(tpep_pickup_datetime AS DATE) as "day",
    COUNT(DISTINCT t."DOLocationID") as nDOL
FROM
    ny_taxi_trips t
LEFT JOIN taxi_zones zpu
    ON t."PULocationID" = zpu."LocationID"
LEFT JOIN taxi_zones zdo
    ON t."DOLocationID" = zpo."LocationID"
WHERE t."PULocationID" = 43
GROUP BY
    CAST(tpep_pickup_datetime AS DATE)
ORDER BY "day" ASC;
```

**Note about quotes in postgres**
`In PostgreSQL, double quotes (like "a red dog") are always used to denote delimited identifiers. In this context, an identifier is the name of an object within PostgreSQL, such as a table name or a column name. Delimited identifiers are identifiers that have a specifically marked beginning and end.`

`Single quotes, on the other hand, are used to indicate that a token is a string. This is used in many different contexts throughout PostgreSQL.`


**The frequency of drop off locations from central park on the 14.1.2021**
```SQL
SELECT
    CONCAT(zdo."Borough", '/', zdo."Zone") AS "dropoff_loc",
    COUNT(t."DOLocationID") as nDrops
FROM
    ny_taxi_trips t
LEFT JOIN taxi_zones zpu
    ON t."PULocationID" = zpu."LocationID"
LEFT JOIN taxi_zones zdo
    ON t."DOLocationID" = zdo."LocationID"
WHERE t."PULocationID" = 43 AND CAST(tpep_pickup_datetime AS DATE) = '2021-01-14'
GROUP BY
    "dropoff_loc"
ORDER BY nDrops DESC;
```

**Average fare/total_amount for a each direction (pickup / drop off)**
```SQL
SELECT
    CONCAT(zpu."Zone", '/', zdo."Zone") AS "direction",
    AVG(t."total_amount") AS avg_fare
FROM
    ny_taxi_trips t
LEFT JOIN taxi_zones zpu
    ON t."PULocationID" = zpu."LocationID"
LEFT JOIN taxi_zones zdo
    ON t."DOLocationID" = zdo."LocationID"
GROUP BY
    "direction"
ORDER BY "avg_fare" DESC;
```

`
Port Richmond/Arden Heights
`