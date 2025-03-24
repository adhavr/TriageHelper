import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.svm import LinearSVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
import joblib


# Load dataset
file_path = "data.csv"
df = pd.read_csv(file_path)

# Convert numeric columns to appropriate types
numeric_cols = ["SBP", "DBP", "HR", "RR", "BT"]
df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

# Drop rows with missing values
df = df.dropna()

# Split features and target
X = df.drop(columns=['KTAS_expert'])
y = df['KTAS_expert']

# Reduce labels by 1 (adjust if needed)
y = y - 1

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale features (recommended for SVM, KNN, and XGBoost)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Function to evaluate models
def evaluate_model(model, X_train, X_test, y_train, y_test, model_name):
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    exact_acc = accuracy_score(y_test, y_pred)

    print(f"{model_name} Accuracy (Exact Match): {exact_acc:.4f}")

    return model, y_pred

# Train and evaluate models
rf_model, y_pred_rf = evaluate_model(RandomForestClassifier(random_state=42),
                                     X_train, X_test, y_train, y_test, "RandomForest")

svc_model, y_pred_svc = evaluate_model(LinearSVC(random_state=42, max_iter=10000),
                                       X_train_scaled, X_test_scaled, y_train, y_test, "LinearSVC")

knn_model, y_pred_knn = evaluate_model(KNeighborsClassifier(n_neighbors=5),
                                       X_train_scaled, X_test_scaled, y_train, y_test, "KNN")

# Create and evaluate Voting Classifier
voting_model = VotingClassifier(estimators=[
    ('rf', rf_model),
    ('svc', svc_model),
    ('knn', knn_model),
], voting='hard')

voting_model, y_pred_voting = evaluate_model(voting_model,
                                             X_train_scaled, X_test_scaled, y_train, y_test, "Voting Classifier")


joblib.dump(voting_model, 'voting_model.pkl')
joblib.dump(scaler, 'scaler.pkl')
joblib.dump(X_train.columns, 'feature_names.pkl')