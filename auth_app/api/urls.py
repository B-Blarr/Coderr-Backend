from django.urls import path
from .views import RegistrationView, CustomLoginView, ProfileDetailView,\
    BusinessProfileView, CustomerProfileView

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('profile/<int:pk>/', ProfileDetailView.as_view(), name='profile-detail'),
    path('profiles/business/', BusinessProfileView.as_view(), name='business-profile-list'),
    path('profiles/customer/', CustomerProfileView.as_view(), name='customer-profile-list'),
]