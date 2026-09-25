import os

import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+psycopg2://grocery_user:grocery_password@localhost:5432/grocery_project"
)

grocery_sales = pd.read_sql("SELECT * FROM grocery_sales", engine)

TRANSFORMED_COLUMNS = [
    "Store_ID",
    "Month",
    "Dept",
    "IsHoliday",
    "Weekly_Sales",
    "CPI",
    "Unemployment",
]

def extract(store_data, extra_data):
    extra_df = pd.read_parquet(extra_data)
    merged_df = store_data.merge(extra_df, on="index")
    return merged_df


merged_df = extract(grocery_sales, "extra_data.parquet")

def transform(raw_data):
    raw_data = raw_data.fillna(0)
    raw_data['Month'] = pd.to_datetime(raw_data['Date'], errors='coerce').dt.month
    raw_data = raw_data.loc[raw_data['Weekly_Sales'] > 10_000]
    raw_data = raw_data.loc[:, TRANSFORMED_COLUMNS]

    return raw_data

clean_data = transform(merged_df)

def avg_weekly_sales_per_month(clean_data):
    return (
        clean_data[["Month", "Weekly_Sales"]]
        .groupby("Month")
        .agg(Avg_Sales=("Weekly_Sales", "mean"))
        .reset_index()
        .round(2)
    )

agg_data = avg_weekly_sales_per_month(clean_data)

def load(full_data, full_data_file_path, agg_data, agg_data_file_path):
    full_data.to_csv(full_data_file_path, index=False)
    agg_data.to_csv(agg_data_file_path, index=False)

load(
    clean_data, "clean_data.csv", agg_data, "agg_data.csv"
)

def validation(file_path):
    return os.path.exists(file_path)

print(validation("clean_data.csv"))
print(validation("agg_data.csv"))
