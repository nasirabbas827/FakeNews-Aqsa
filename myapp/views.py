from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.conf import settings
from django.utils import timezone
from .models import CustomerUser, NewsAnalysis, SystemUsageLog
from .forms import RegisterForm, LoginForm, EditProfileForm, NewsAnalysisForm
import joblib
import os
import re

# =========================
# Preprocess Input Text
# =========================
def preprocess_input_text(text):
    text = str(text)
    text = re.sub(r"[\u2018\u2019]", "'", text)
    text = re.sub(r"[\u201c\u201d]", '"', text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# =========================
# AUTHENTICATION VIEWS
# =========================

def index(request):
    return render(request, 'index.html')


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully. Please login.")
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                user = CustomerUser.objects.get(username=username)
                if user.status != 'active':
                    messages.error(request, "Your account is not active. Please contact support.")
                elif check_password(password, user.password):
                    request.session['user_id'] = user.user_id
                    request.session['username'] = user.username
                    messages.success(request, f"Welcome {user.username}!")
                    return redirect('dashboard')
                else:
                    messages.error(request, "Invalid password")
            except CustomerUser.DoesNotExist:
                messages.error(request, "User not found")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    request.session.flush()
    messages.success(request, "You have been logged out.")
    return redirect('index')


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import CustomerUser, NewsAnalysis, SystemUsageLog, Dataset
from .forms import NewsAnalysisForm
import joblib
import os
import re

def preprocess_input_text(text):
    """Clean up input text for prediction"""
    text = str(text)
    text = re.sub(r"[\u2018\u2019]", "'", text)
    text = re.sub(r"[\u201c\u201d]", '"', text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def get_client_ip(request):
    """Retrieve client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def dashboard_view(request):
    if 'user_id' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login')

    user = CustomerUser.objects.get(user_id=request.session['user_id'])
    prediction_result = None
    datasets = Dataset.objects.all().order_by('-uploaded_at')  # list datasets for testing

    if request.method == "POST":
        form = NewsAnalysisForm(request.POST)
        if form.is_valid():
            news_text = form.cleaned_data['news_text']
            news_text_processed = preprocess_input_text(news_text)

            # Load latest models
            models_dir = os.path.join(settings.MEDIA_ROOT, "trained_models")
            lr_model_path = max(
                [os.path.join(models_dir, f) for f in os.listdir(models_dir) if f.startswith("lr_model_")],
                key=os.path.getctime
            )
            svm_model_path = max(
                [os.path.join(models_dir, f) for f in os.listdir(models_dir) if f.startswith("svm_model_")],
                key=os.path.getctime
            )
            vectorizer_path = max(
                [os.path.join(models_dir, f) for f in os.listdir(models_dir) if f.startswith("vectorizer_")],
                key=os.path.getctime
            )

            lr_model = joblib.load(lr_model_path)
            svm_model = joblib.load(svm_model_path)
            vectorizer = joblib.load(vectorizer_path)

            X_input = vectorizer.transform([news_text_processed])

            lr_pred = int(lr_model.predict(X_input)[0])
            svm_pred = int(svm_model.predict(X_input)[0])

            lr_conf = max(lr_model.predict_proba(X_input)[0])
            svm_conf = max(svm_model.predict_proba(X_input)[0])
            avg_conf = (lr_conf + svm_conf) / 2

            # Save analysis
            NewsAnalysis.objects.create(
                user=user,
                news_text=news_text,
                prediction=lr_pred,
                confidence_score=avg_conf
            )

            ip = get_client_ip(request)
            SystemUsageLog.objects.create(
                user=user,
                action=f"Analyzed news text: {news_text[:50]}...",
                ip_address=ip,
                timestamp=timezone.now()
            )

            prediction_result = {
                'lr': 'Fake' if lr_pred else 'Real',
                'svm': 'Fake' if svm_pred else 'Real',
                'avg_confidence': round(avg_conf*100, 2)
            }
    else:
        form = NewsAnalysisForm()

    return render(request, 'dashboard.html', {
        'user': user,
        'form': form,
        'prediction_result': prediction_result,
        'datasets': datasets
    })


# =========================
# PROFILE MANAGEMENT
# =========================
def edit_profile(request):
    if not request.session.get('user_id'):
        messages.error(request, "You need to log in first.")
        return redirect('login')

    user = get_object_or_404(CustomerUser, pk=request.session['user_id'])
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('dashboard')
    else:
        form = EditProfileForm(instance=user)

    return render(request, 'edit_profile.html', {
        'form': form,
        'user': user,
    })


# =========================
# HELPER FUNCTION
# =========================
def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip



from django.shortcuts import render, redirect
from django.contrib import messages
from .models import NewsAnalysis, CustomerUser

def news_history_view(request):
    """Display logged-in user's news analysis history."""
    if 'user_id' not in request.session:
        messages.error(request, "Please login first to view your analysis history.")
        return redirect('login')

    user = CustomerUser.objects.get(user_id=request.session['user_id'])
    history = NewsAnalysis.objects.filter(user=user).order_by('-analyzed_at')

    # Prepare counts for Plotly charts
    real_count = history.filter(prediction=0).count()
    fake_count = history.filter(prediction=1).count()
    confidence_list = list(history.values_list('confidence_score', flat=True))
    date_labels = [record.analyzed_at.strftime("%b %d %H:%M") for record in history]

    return render(request, 'news_history.html', {
        'user': user,
        'history': history,
        'real_count': real_count,
        'fake_count': fake_count,
        'confidence_list': confidence_list,
        'date_labels': date_labels
    })


import csv
from django.http import HttpResponse

def export_news_history_csv(request):
    if 'user_id' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login')

    user = CustomerUser.objects.get(user_id=request.session['user_id'])
    history = NewsAnalysis.objects.filter(user=user).order_by('-analyzed_at')

    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="analysis_history.csv"'

    writer = csv.writer(response)
    # Write CSV headers
    writer.writerow(['News Text', 'Verdict', 'Confidence Score', 'Date', 'Time'])

    # Write data rows
    for record in history:
        verdict = 'Fake' if record.prediction == 1 else 'Real'
        date = record.analyzed_at.strftime("%Y-%m-%d")
        time = record.analyzed_at.strftime("%H:%M")
        writer.writerow([record.news_text, verdict, record.confidence_score, date, time])

    return response


from django.shortcuts import render
from django.contrib import messages
from .models import Dataset

def dataset_list_view(request):
    """Display all datasets uploaded by admin for testing."""
    if 'user_id' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login')

    datasets = Dataset.objects.all().order_by('-uploaded_at')

    return render(request, 'dataset_list.html', {
        'datasets': datasets
    })
