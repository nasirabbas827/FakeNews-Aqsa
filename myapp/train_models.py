import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
from datetime import datetime
from django.conf import settings
from .models import Dataset, ModelTrainingLog

# =========================
# Load Dataset Safely
# =========================
def load_dataset(dataset_file_path):
    try:
        # Try utf-8 first
        df = pd.read_csv(dataset_file_path)
    except UnicodeDecodeError:
        # Fall back to latin1 (Windows-1252)
        df = pd.read_csv(dataset_file_path, encoding="latin1", on_bad_lines="skip")
    return df

# =========================
# Preprocess Text
# =========================
def preprocess_text(df, text_column='text'):
    df[text_column] = df[text_column].astype(str)
    # Normalize quotes, remove extra spaces
    df[text_column] = df[text_column].str.replace(r"[\u2018\u2019]", "'", regex=True)
    df[text_column] = df[text_column].str.replace(r"[\u201c\u201d]", '"', regex=True)
    df[text_column] = df[text_column].str.replace(r"\s+", " ", regex=True)
    df[text_column] = df[text_column].str.strip()
    return df

# =========================
# Train Models
# =========================
def train_models(dataset_obj):
    """
    Trains Logistic Regression and SVM models on the provided Dataset object.
    Saves trained models, vectorizer, and logs metrics in ModelTrainingLog.
    Returns dictionary with metrics and saved file paths.
    """
    file_path = os.path.join(settings.MEDIA_ROOT, dataset_obj.file.name)
    df = load_dataset(file_path)
    df = preprocess_text(df)

    # Map labels to 0/1
    df['label'] = df['label'].map(lambda x: 1 if str(x).strip().upper() == 'FAKE' else 0)

    X = df['text']
    y = df['label']

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    # ========================
    # Logistic Regression
    # ========================
    lr_model = LogisticRegression(max_iter=500)
    lr_model.fit(X_train_vec, y_train)
    y_pred_lr = lr_model.predict(X_test_vec)
    lr_metrics = {
        'accuracy': accuracy_score(y_test, y_pred_lr),
        'precision': precision_score(y_test, y_pred_lr),
        'recall': recall_score(y_test, y_pred_lr),
        'f1_score': f1_score(y_test, y_pred_lr)
    }

    # ========================
    # Support Vector Machine
    # ========================
    svm_model = SVC(kernel='linear', probability=True)
    svm_model.fit(X_train_vec, y_train)
    y_pred_svm = svm_model.predict(X_test_vec)
    svm_metrics = {
        'accuracy': accuracy_score(y_test, y_pred_svm),
        'precision': precision_score(y_test, y_pred_svm),
        'recall': recall_score(y_test, y_pred_svm),
        'f1_score': f1_score(y_test, y_pred_svm)
    }

    # ========================
    # Save models & vectorizer
    # ========================
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    models_dir = os.path.join(settings.MEDIA_ROOT, "trained_models")
    os.makedirs(models_dir, exist_ok=True)

    lr_path = os.path.join(models_dir, f"lr_model_{timestamp}.joblib")
    svm_path = os.path.join(models_dir, f"svm_model_{timestamp}.joblib")
    vec_path = os.path.join(models_dir, f"vectorizer_{timestamp}.joblib")

    joblib.dump(lr_model, lr_path)
    joblib.dump(svm_model, svm_path)
    joblib.dump(vectorizer, vec_path)

    # ========================
    # Save Training Logs in DB
    # ========================
    ModelTrainingLog.objects.create(
        dataset=dataset_obj,
        model_name='logistic_regression',
        accuracy=lr_metrics['accuracy'],
        precision=lr_metrics['precision'],
        recall=lr_metrics['recall'],
        f1_score=lr_metrics['f1_score']
    )

    ModelTrainingLog.objects.create(
        dataset=dataset_obj,
        model_name='svm',
        accuracy=svm_metrics['accuracy'],
        precision=svm_metrics['precision'],
        recall=svm_metrics['recall'],
        f1_score=svm_metrics['f1_score']
    )

    # ========================
    # Return metrics and paths
    # ========================
    return {
        'logistic_regression': lr_metrics,
        'svm': svm_metrics,
        'lr_model_path': lr_path,
        'svm_model_path': svm_path,
        'vectorizer_path': vec_path
    }
