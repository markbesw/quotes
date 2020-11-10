
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    path('register', views.register),
    path('login', views.login),
    path('quotes', views.quotes),
    path('create_quote', views.create_quote),
    path('logout', views.logout),
    path('user/<int:user_id>', views.user),
    path('myaccount/<int:user_id>', views.myaccount),
    path('update_account', views.update_account),
    path('acct_error', views.acct_error),
    path('delete_post/<int:quote_id>', views.delete_post)
]
