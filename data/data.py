import os
import geopandas as gpd
import matplotlib.pyplot as plt
import psycopg2

def download_data():
    os.system("sh data/download.sh")

def load_data():
    
    dataframes = {}
    for file in os.listdir("./"):
        if file.endswith(".json"):
            print(f"Processing {file}")
            df = gpd.read_file(f"./{file}")
            if df.empty:
                print(f"Skipping {file} because it's empty")
                continue
            df_name = f"df_{file.split('-')[1].split('.')[0]}"
            dataframes[df_name] = df

        
    return dataframes

def connect_to_postgis():
    con = psycopg2.connect(
        host="localhost",
        database="overture",
        user="mapper",
        password="password"
    )
    return con

def df_to_postgis(df, name):
    con = connect_to_postgis()
    df.to_postgis(name, con, if_exists="replace")

# def dump_data(output_file):
#     # con = connect_to_postgis()
#     os.system(f"pg_dump -U mapper -d overture -f {output_file}")

if __name__ == "__main__":
    print(load_data())