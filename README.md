# Fake News Aqsa

FakeNews-Aqsa is a machine-learning application for news text classification.

![Django](https://img.shields.io/badge/Django-2563EB?style=flat-square) ![SQLite](https://img.shields.io/badge/SQLite-0F172A?style=flat-square)

## Overview

The data model covers `CustomerUser`, `Dataset`, `ModelTrainingLog`, `NewsAnalysis`, `SystemUsageLog`.

## Implemented workflows

The source defines these handlers:

- **Index** — `index`
- **Register** — `register_view`
- **Login** — `login_view`
- **Logout** — `logout_view`
- **Get Client Ip** — `get_client_ip`
- **Dashboard** — `dashboard_view`
- **Edit Profile** — `edit_profile`
- **News History** — `news_history_view`
- **Export News History Csv** — `export_news_history_csv`
- **Dataset List** — `dataset_list_view`

## Getting started

### 1. Get the project

```bash
git clone https://github.com/nasirabbas827/FakeNews-Aqsa.git
cd FakeNews-Aqsa
```

### 2. Prepare Python

Create an isolated environment:

```bash
python -m venv .venv
```

Activate it with `.venv\Scripts\activate` on Windows Command Prompt, or `source .venv/bin/activate` on macOS/Linux.

No requirements file is included. The inspected Python imports indicate these dependencies as a starting point:

```bash
python -m pip install Django joblib pandas scikit-learn Pillow
```

Dependency versions are not pinned in this repository.

### 3. Configure and run

Review [`myproject/settings.py`](myproject/settings.py) for database, media, and any email configuration. Use a local copy of the supplied database when available.

```bash
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000/. If you need a Django administration account, run `python manage.py createsuperuser`. Application-specific user roles may be managed separately.

Review the application's email/API configuration and supply your own service credentials for integrations you intend to use.

### Model files

Included artifacts: [`trained_models/lr_model_20260218211727.joblib`](trained_models/lr_model_20260218211727.joblib), [`trained_models/svm_model_20260218211727.joblib`](trained_models/svm_model_20260218211727.joblib), [`trained_models/vectorizer_20260218211727.joblib`](trained_models/vectorizer_20260218211727.joblib).

Keep models, preprocessing objects, and label mappings together in the locations expected by the source.

## Repository guide

| Path | Purpose |
| --- | --- |
| [`datasets`](datasets) | Dataset resources |
| [`db.sqlite3`](db.sqlite3) | Included SQLite database |
| [`manage.py`](manage.py) | Django command-line entry point |
| [`myapp`](myapp) | Django application modules |
| [`myproject`](myproject) | Django project configuration |
| [`templates`](templates) | HTML page templates |
| [`trained_models`](trained_models) | Saved model artifacts |

## Development notes

These setup instructions are based on the repository source. The application has not been executed as part of this documentation update; verify dependencies and configuration in your local environment.
