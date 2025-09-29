
from django.urls import path
from. import views
urlpatterns = [
    path('login/',views.loginView, name='client-login'),
    path('signup/',views.signUp,name='client_signUp'),
    path("logout/", views.logoutPage, name='client-logout'),
    path("transfer/", views.transferPage, name='client-transfer'),
    path("profile/", views.profilePage, name='client-page'),
    path("", views.dashboardPage, name='client-dashboard'),
    path("transactions/", views.transactionPage, name='client-transactions'),
    path("pin/", views.pinPage, name='client-pin'),
    path("usersearch/",views.searchUser, name='Client-search-page')
]



#  path('', views.cardPurchaseEndpoint,name='card_purchase'),
#     path("profiles/", views.getAllProfile, name='profilepage'),
#     path("profile/", views.profilePage,name='client-page'),