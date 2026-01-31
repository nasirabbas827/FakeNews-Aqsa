from django.db import models
from django.utils import timezone



# =====================================================
# Custom User Model (Simple, Admin-Managed)
# =====================================================
class CustomerUser(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('banned', 'Banned'),
    )

    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    full_name = models.CharField(max_length=150, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(
        max_length=10,
        choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
        blank=True,
        null=True
    )
    dob = models.DateField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    last_login = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username


# =====================================================
# Dataset Uploaded by Admin (CSV)
# =====================================================
class Dataset(models.Model):
    name = models.CharField(max_length=200)
    file = models.FileField(upload_to='datasets/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# =====================================================
# Model Training Logs (REAL METRICS)
# =====================================================
class ModelTrainingLog(models.Model):
    MODEL_CHOICES = (
        ('logistic_regression', 'Logistic Regression'),
        ('svm', 'Support Vector Machine'),
    )

    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='training_logs')
    model_name = models.CharField(max_length=50, choices=MODEL_CHOICES)

    accuracy = models.FloatField()
    precision = models.FloatField()
    recall = models.FloatField()
    f1_score = models.FloatField()

    trained_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-trained_at']
        unique_together = ('dataset', 'model_name', 'trained_at')

    def __str__(self):
        return f"{self.get_model_name_display()} | {self.dataset.name}"


# =====================================================
# User News Analysis History (Prediction Results)
# =====================================================
class NewsAnalysis(models.Model):
    RESULT_CHOICES = (
        (0, 'Real'),
        (1, 'Fake'),
    )

    user = models.ForeignKey(CustomerUser, on_delete=models.CASCADE)
    news_text = models.TextField()
    prediction = models.IntegerField(choices=RESULT_CHOICES)
    confidence_score = models.FloatField()
    analyzed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-analyzed_at']

    def __str__(self):
        return f"{self.user.username} - {self.get_prediction_display()}"


class SystemUsageLog(models.Model):
    user = models.ForeignKey(CustomerUser, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.action