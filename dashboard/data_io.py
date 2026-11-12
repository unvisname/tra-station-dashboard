from pathlib import Path
import pandas as pd
import streamlit as st

from style import CLUSTER_ID

BASE = Path(__file__).resolve().parent.parent
PROC = BASE / "data" / "processed"
REP = BASE / "reports"


@st.cache_data
def load_clusters() -> pd.DataFrame:
    df = pd.read_csv(PROC / "station_clusters.csv", dtype={"sta_code": str})
    df["size_band"] = (df["mean_total"] >= 10000).map({True: ">=10000", False: "<10000"})
    return df


@st.cache_data
def load_profile() -> pd.DataFrame:
    df = pd.read_csv(REP / "cluster_profile.csv")
    df["cluster_name"] = df["cluster"].map(CLUSTER_ID)
    return df


@st.cache_data
def load_daily() -> pd.DataFrame:
    df = pd.read_csv(REP / "case_daily_4stations.csv")
    df["date"] = pd.to_datetime(df["date"])
    return df


@st.cache_data
def load_summary() -> pd.DataFrame:
    return pd.read_csv(REP / "case_stations_summary.csv")


@st.cache_data
def load_livingarea() -> pd.DataFrame:
    pop = pd.read_csv(REP / "livingarea_pop_4stations.csv")
    osm = pd.read_csv(REP / "livingarea_osm_poi_4stations.csv")
    plvr = pd.read_csv(REP / "livingarea_plvr_4districts.csv")

    pop = pop[pop["level"] == "minstat"]

    def pick(df, radius, col, newname):
        return (df[df["radius_m"] == radius]
                .set_index("station")[col]
                .rename(newname))

    out = pd.concat([
        pick(pop, 500, "pop_area_weighted", "pop_500"),
        pick(pop, 1000, "pop_area_weighted", "pop_1km"),
        pick(osm, 1000, "total_elements", "poi_1km"),
        pick(osm, 1000, "food_cafe_restaurant_fastfood", "food_1km"),
        pick(osm, 500, "shop_convenience", "conv_500"),
        plvr.set_index("station")[["median_price_per_ping_all", "n_building_deals", "town"]]
            .rename(columns={"median_price_per_ping_all": "price_ping",
                             "n_building_deals": "price_n"}),
    ], axis=1)

    return out.reset_index()


@st.cache_data
def load_business() -> pd.DataFrame:
    return pd.read_csv(PROC / "cluster_business_table.csv")


ADVICE_COLS = ["cluster_name", "subtype", "main_proposal", "flow_profile",
               "suitable", "unsuitable", "reference", "example_stations"]


@st.cache_data
def load_station() -> pd.DataFrame:
    return pd.read_csv(PROC / "dashboard_station.csv", dtype={"sta_code": str})


@st.cache_data
def load_subtype_rules() -> pd.DataFrame:
    df = pd.read_csv(PROC / "subtype_rules.csv", dtype={"or_group": str})
    df["or_group"] = df["or_group"].fillna("")
    return df


@st.cache_data
def load_subtype_advice() -> pd.DataFrame:
    path = PROC / "subtype_advice.csv"
    if not path.exists():
        return pd.DataFrame(columns=ADVICE_COLS)
    return pd.read_csv(path, dtype=str).fillna("")


@st.cache_data
def load_daily_all() -> pd.DataFrame:
    df = pd.read_parquet(PROC / "daily_235.parquet")
    df["sta_code"] = df["sta_code"].astype(str)
    return df