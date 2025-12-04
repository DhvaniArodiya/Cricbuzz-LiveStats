import os
import pandas as pd
import numpy as np

DATA_RAW = "india_housing_prices.csv"
DATA_PROCESSED = "india_housing_prices.csv"

def count_amenities(x):
    if pd.isna(x) or str(x).strip() == "":
        return 0
    return len([a for a in str(x).split(",") if a.strip() != ""])

def load_raw_data(path=DATA_RAW):
    df = pd.read_csv(path)
    df = df.drop_duplicates()
    if "ID" in df.columns:
        df = df.drop(columns=["ID"])
    return df

def basic_cleaning(df: pd.DataFrame) -> pd.DataFrame:
    # simple missing value handling
    for col in df.select_dtypes(include=[np.number]).columns:
        df[col] = df[col].fillna(df[col].median())
    for col in df.select_dtypes(exclude=[np.number]).columns:
        df[col] = df[col].fillna(df[col].mode()[0])
    return df

def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    # price per sqft
    if "Price_per_SqFt" not in df.columns:
        df["Price_per_SqFt"] = (
            df["Price_in_Lakhs"] * 100000 / df["Size_in_SqFt"].clip(lower=1)
        )

    # amenity count
    if "Amenities" in df.columns:
        df["Amenity_Count"] = df["Amenities"].apply(count_amenities)
        df = df.drop(columns=["Amenities"])
    else:
        df["Amenity_Count"] = 0

    # binary features
    df["Is_Furnished"] = df["Furnished_Status"].isin(["Furnished", "Semi-furnished"]).astype(int)

    df["Is_Ready_To_Move"] = df["Availability_Status"].astype(str).str.lower().str.contains("ready").astype(int)

    df["Has_Parking"] = df["Parking_Space"].astype(str).str.lower().isin(
        ["yes", "covered", "open"]
    ).astype(int)

    if "Security" in df.columns:
        df["Has_Security"] = df["Security"].astype(str).str.lower().isin(
            ["yes", "24x7", "gated"]
        ).astype(int)
    else:
        df["Has_Security"] = 0

    facing_map = {"North": 0, "East": 1, "West": 2, "South": 3}
    df["Facing_Code"] = df["Facing"].map(facing_map)

    if "Age_of_Property" not in df.columns and "Year_Built" in df.columns:
        df["Age_of_Property"] = 2025 - df["Year_Built"]

    df["School_Density_Score"] = df["Nearby_Schools"] / 10.0
    df["Hospital_Density_Score"] = df["Nearby_Hospitals"] / 10.0

    return df

def create_targets(df: pd.DataFrame) -> pd.DataFrame:
    # Good_Investment classification
    city_median_price = df.groupby("City")["Price_in_Lakhs"].median()
    city_median_pps = df.groupby("City")["Price_per_SqFt"].median()

    def investment_score(row):
        score = 0
        if row["Price_in_Lakhs"] <= city_median_price[row["City"]]:
            score += 1
        if row["Price_per_SqFt"] <= city_median_pps[row["City"]]:
            score += 1
        if row["BHK"] >= 3:
            score += 1
        if row["Is_Ready_To_Move"] == 1:
            score += 1
        if row["Has_Parking"] == 1:
            score += 1
        if row["Public_Transport_Accessibility"] in ["Medium", "High"]:
            score += 1
        return score

    df["Investment_Score"] = df.apply(investment_score, axis=1)
    df["Good_Investment"] = (df["Investment_Score"] >= 3).astype(int)

    # Future price regression
    growth_map = {"Low": 0.06, "Medium": 0.08, "High": 0.10}

    def future_price(row, years=5):
        r = growth_map.get(row["Public_Transport_Accessibility"], 0.08)
        return row["Price_in_Lakhs"] * ((1 + r) ** years)

    df["Future_Price_5Y"] = df.apply(future_price, axis=1)

    return df

def main():
    os.makedirs("data", exist_ok=True)

    df = load_raw_data()
    df = basic_cleaning(df)
    df = feature_engineering(df)
    df = create_targets(df)

    df.to_csv(DATA_PROCESSED, index=False)
    print(f"Processed data saved to {DATA_PROCESSED}")

if __name__ == "__main__":
    main()
