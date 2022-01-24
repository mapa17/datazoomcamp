from optparse import Option
from pathlib import Path
from typing import Optional

import pandas as pd
from sqlalchemy import create_engine

import typer


def main(filename : Path,
    table_name : str, 
    username : Optional[str] = typer.Argument("root"),
    password : Optional[str] = typer.Argument("root"),
    host : Optional[str] = typer.Argument("localhost"),
    port : Optional[str] = typer.Argument("5432"),
    db : Optional[str] = typer.Argument("ny_taxi"),
    ):

    # Use sqlalchemy to access the db
    engine = create_engine(f'postgresql://{username}:{password}@{host}:{port}/{db}')

    # Read 100 rows for datatypes
    df = pd.read_csv(filename, nrows=100)

    # Write the table structure based on the dataframe header
    if 'tpep_pickup_datime' in df:
        df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
        df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
    df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')

    print("Inserting data into databse ...")
    df_iter = pd.read_csv(filename, iterator=True, chunksize=100_000)
    for df in df_iter:    
        if 'tpep_pickup_datime' in df:
            df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
            df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

        df.to_sql(name=table_name, con=engine, if_exists='append')

        print('inserted another chunk ...')
    print(f"Finished writing {filename} to {db} ...")



if __name__ == "__main__":
    typer.run(main)

