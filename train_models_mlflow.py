import os
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score, f1_score, confusion_matrix,
    mean_squared_error, mean_absolute_error, r2_score
)
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
import joblib

import mlflow
import mlflow.sklearn


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_PROCESSED = os.path.join(BASE_DIR, "india_housing_prices.csv")
MODELS_DIR = os.path.join(BASE_DIR, "models")

os.makedirs(MODELS_DIR, exist_ok=True)


def load_processed():
    print("Loading processed data from:", DATA_PROCESSED)
    df = pd.read_csv(DATA_PROCESSED)
    return df


def build_preprocessor():
    numeric_features = [
        "BHK","Size_in_SqFt","Price_in_Lakhs","Price_per_SqFt",
        "Year_Built","Floor_No","Total_Floors","Age_of_Property",
        "Nearby_Schools","Nearby_Hospitals",
        "Amenity_Count","Is_Furnished","Is_Ready_To_Move",
        "Has_Parking","Has_Security",
        "School_Density_Score","Hospital_Density_Score",
        "Facing_Code"
    ]

    categorical_features = [
        "State","City","Locality","Property_Type",
        "Furnished_Status","Public_Transport_Accessibility",
        "Parking_Space","Security","Facing",
        "Owner_Type","Availability_Status"
    ]

    numeric_transformer = Pipeline(steps=[
        ("scaler", StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ("onehot", OneHotEncoder(handle_unknown="ignore"))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features)
        ]
    )

    return preprocessor, numeric_features + categorical_features


def train_classification(X, y, preprocessor):
    model = RandomForestClassifier(
        n_estimators=300, random_state=42, n_jobs=-1
    )

    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)

    print("Classification Accuracy:", acc)
    print("F1-score:", f1)
    print("Confusion Matrix:\n", cm)

    with mlflow.start_run(run_name="classification_model"):
        mlflow.log_param("model_type", "RandomForestClassifier")
        mlflow.log_metric("accuracy", acc)
        mlflow.log_metric("f1_score", f1)
        mlflow.sklearn.log_model(pipeline, "classification_model")

    return pipeline


def train_regression(X, y, preprocessor):
    model = RandomForestRegressor(
        n_estimators=300, random_state=42, n_jobs=-1
    )

    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    rmse = mean_squared_error(y_test, y_pred, squared=False)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print("Regression RMSE:", rmse)
    print("MAE:", mae)
    print("R²:", r2)

    with mlflow.start_run(run_name="regression_model"):
        mlflow.log_param("model_type", "RandomForestRegressor")
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("mae", mae)
        mlflow.log_metric("r2", r2)
        mlflow.sklearn.log_model(pipeline, "regression_model")

    return pipeline


def main():
    mlflow.set_experiment("real_estate_investment")

    df = load_processed()
    preprocessor, feature_cols = build_preprocessor()

    X = df[feature_cols]
    y_cls = df["Good_Investment"]
    y_reg = df["Future_Price_5Y"]

    cls_pipeline = train_classification(X, y_cls, preprocessor)
    reg_pipeline = train_regression(X, y_reg, preprocessor)

    cls_path = os.path.join(MODELS_DIR, "good_investment_classifier.joblib")
    reg_path = os.path.join(MODELS_DIR, "future_price_regressor.joblib")

    joblib.dump(cls_pipeline, cls_path)
    joblib.dump(reg_pipeline, reg_path)

    print("Models saved to:")
    print("  ", cls_path)
    print("  ", reg_path)


if __name__ == "__main__":
    main()