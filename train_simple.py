import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import accuracy_score, f1_score, mean_squared_error, r2_score
import joblib

# ------------------ PATHS ------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "india_housing_prices.csv")
MODELS_DIR = os.path.join(BASE_DIR, "models")

os.makedirs(MODELS_DIR, exist_ok=True)

print("Loading data from:", DATA_PATH)
df = pd.read_csv(DATA_PATH)
print("Original data shape:", df.shape)

# ---- SPEED TRICK: use a subset of data ----
MAX_ROWS = 3000   # you can make this 1000 if still slow

if len(df) > MAX_ROWS:
    df = df.sample(MAX_ROWS, random_state=42).reset_index(drop=True)
    print("Using subset of data:", df.shape)

# ------------------ FEATURES & TARGETS ------------------

target_cls = "Good_Investment"
target_reg = "Future_Price_5Y"

numeric_features = [
    "BHK","Size_in_SqFt","Price_in_Lakhs","Price_per_SqFt",
    "Year_Built","Floor_No","Total_Floors","Age_of_Property",
    "Nearby_Schools","Nearby_Hospitals",
    "Amenity_Count","Is_Furnished","Is_Ready_To_Move",
    "Has_Parking","Has_Security",
    "School_Density_Score","Hospital_Density_Score",
    "Facing_Code"
]

# IMPORTANT: we DROP Locality here to avoid huge one-hot (much faster)
categorical_features = [
    "State","City","Property_Type",
    "Furnished_Status","Public_Transport_Accessibility",
    "Parking_Space","Security","Facing",
    "Owner_Type","Availability_Status"
]

feature_cols = numeric_features + categorical_features

X = df[feature_cols]
y_cls = df[target_cls]
y_reg = df[target_reg]

# ------------------ PREPROCESSOR ------------------

numeric_transformer = Pipeline(steps=[
    ("scaler", StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ("onehot", OneHotEncoder(handle_unknown="ignore"))
])

preprocessor = ColumnTransformer(
    transformers=[
        ("num", numeric_transformer, numeric_features),
        ("cat", categorical_transformer, categorical_features),
    ]
)

# ------------------ CLASSIFICATION MODEL (FAST) ------------------

print("\n=== Training FAST CLASSIFICATION model (LogisticRegression) ===")
cls_model = LogisticRegression(
    max_iter=1000   # more iterations but still very fast
)

cls_pipeline = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("model", cls_model),
])

X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(
    X, y_cls, test_size=0.2, random_state=42, stratify=y_cls
)

cls_pipeline.fit(X_train_c, y_train_c)
y_pred_c = cls_pipeline.predict(X_test_c)
acc = accuracy_score(y_test_c, y_pred_c)
f1 = f1_score(y_test_c, y_pred_c)
print("Classification accuracy (fast):", acc)
print("Classification F1 (fast):", f1)

cls_path = os.path.join(MODELS_DIR, "good_investment_classifier.joblib")
joblib.dump(cls_pipeline, cls_path)
print(" Saved classifier to:", cls_path)

# ------------------ REGRESSION MODEL (FAST) ------------------

print("\n=== Training FAST REGRESSION model (LinearRegression) ===")
reg_model = LinearRegression()

reg_pipeline = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("model", reg_model),
])

# handle NaNs just in case
mask = ~y_reg.isna()
X_reg = X[mask]
y_reg_clean = y_reg[mask]

X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(
    X_reg, y_reg_clean, test_size=0.2, random_state=42
)

reg_pipeline.fit(X_train_r, y_train_r)
y_pred_r = reg_pipeline.predict(X_test_r)

mse = mean_squared_error(y_test_r, y_pred_r)
rmse = mse ** 0.5
r2 = r2_score(y_test_r, y_pred_r)

print("Regression RMSE (fast):", rmse)
print("Regression R² (fast):", r2)

reg_path = os.path.join(MODELS_DIR, "future_price_regressor.joblib")
joblib.dump(reg_pipeline, reg_path)
print(" Saved regressor to:", reg_path)

print("\n FAST training finished. Check the 'models' folder.")
