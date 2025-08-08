from django.urls import path
from users.views import signup_view, login_view, logout_view, activate_account

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('activate/<uidb64>/<token>/', activate_account, name='activate')
]