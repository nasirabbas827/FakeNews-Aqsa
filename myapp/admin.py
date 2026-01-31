from django.contrib import admin
from .models import Dataset, ModelTrainingLog, CustomerUser, NewsAnalysis , SystemUsageLog
from .train_models import train_models


from django.contrib import admin
from .models import Dataset, ModelTrainingLog, CustomerUser
from .train_models import train_models  # <- updated import

# --------------------------------------------------
# Customer User Admin
# --------------------------------------------------
@admin.register(CustomerUser)
class CustomerUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'username', 'email', 'status')
    search_fields = ('username', 'email')
    list_filter = ('status',)


# --------------------------------------------------
# Dataset Admin (TRAIN ACTION)
# --------------------------------------------------
@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'uploaded_at')
    actions = ['train_dataset_models']

    def train_dataset_models(self, request, queryset):
        for dataset in queryset:
            # Just pass the dataset object
            results = train_models(dataset)

        self.message_user(request, "Dataset trained successfully using ML models.")

    train_dataset_models.short_description = "Trigger Model Training"


# --------------------------------------------------
# Training Logs Admin
# --------------------------------------------------
@admin.register(ModelTrainingLog)
class ModelTrainingLogAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'model_name',
        'dataset',
        'accuracy',
        'precision',
        'recall',
        'f1_score',
        'trained_at'
    )
    list_filter = ('model_name',)
    ordering = ('-trained_at',)



# --------------------------------------------------
# News Analysis Admin (User Predictions)
# --------------------------------------------------
@admin.register(NewsAnalysis)
class NewsAnalysisAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'prediction', 'confidence_score', 'analyzed_at')
    list_filter = ('prediction',)
    search_fields = ('user__username', 'news_text')
    ordering = ('-analyzed_at',)


# --------------------------------------------------
# System Usage Log Admin
# --------------------------------------------------
@admin.register(SystemUsageLog)
class SystemUsageLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'action', 'ip_address', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('user__username', 'action', 'ip_address')
    ordering = ('-timestamp',)