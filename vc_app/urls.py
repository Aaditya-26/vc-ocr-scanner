from django.urls import path
from . import views

urlpatterns = [
    # ── HTML pages ────────────────────────────────────────────
    path('', views.dashboard, name='dashboard'),
    path('upload/', views.upload_page, name='upload'),
    path('contact/<int:pk>/', views.detail_page, name='detail'),

    # ── REST API ──────────────────────────────────────────────
    path('api/v1/visiting-card/upload/', views.VisitingCardUploadView.as_view(), name='api-upload'),
    path('api/v1/contacts/', views.ContactListView.as_view(), name='api-contacts'),
    path('api/v1/contact/<int:pk>/', views.ContactDetailView.as_view(), name='api-detail'),
    path('api/v1/contact/<int:pk>/delete/', views.ContactDeleteView.as_view(), name='api-delete'),
]
