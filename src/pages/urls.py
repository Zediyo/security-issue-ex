from django.urls import path

from .views import homePageView, transferView, loginPageView, logoutPageView

urlpatterns = [
	path("", loginPageView, name="log-in"),
    path('user/<user>/', homePageView, name='home'),
	path("logout/", logoutPageView, name="logout"),
    path('user/<user>/transfer/', transferView, name='transfer'),
]
