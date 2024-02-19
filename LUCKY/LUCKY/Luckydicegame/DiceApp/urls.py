from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_view
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static

from .forms import LoginForm, MyPasswordResetForm
from .views import BetListCreateView, GameResultListCreateView, WalletListCreateView

urlpatterns = [
    path("", views.index, name="index"),
    path("About/", views.About, name="about"),
    path("How-to-play/", views.How_to_play, name="How-to-play"),
    path("practice_game/", views.practice_game, name="practice_game"),
    path("register/", views.register.as_view(), name="register"),
    path(
        "accounts/login/",
        auth_view.LoginView.as_view(
            template_name="DiceApp/login.html", authentication_form=LoginForm
        ),
        name="login",
    ),
    path(
        "password-reset/",
        auth_view.PasswordResetView.as_view(
            template_name="app/password_reset.html", form_class=MyPasswordResetForm
        ),
        name="password_reset",
    ),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("User_profile/", views.User_profile.as_view(), name="User_profile"),
    path(
        "Profile_settings/",
        views.ProfileSettingsView.as_view(),
        name="Profile_settings",
    ),
    path("mybalance/<str:balance>/", views.Mybalance, name="MyBalance"),
    path('mybalance/', views.Mybalance, name='MyBalanceWithoutBalance'),
    path('check_balance/', views.check_balance, name='check_balance'),
    path('success_page/<str:balance>/', views.success_page, name='success_page'),
    
    path("payment_view", views.payment_view, name="payment_view"),
    path("success/", views.success, name="success"),
    path("initiate_payment", views.initiate_payment, name="initiate_payment"),
    path("payment_view/<str:balance>/", views.payment_view, name="payment_view"),
    path("play_game", views.PlayGameView.as_view(), name="play_game"),
    path("Inbox/", views.Inbox, name="Inbox"),
    path('view_all_deposits/', views.view_all_deposits, name='view_all_deposits'),

    path("Withdraw/", views.Withdraw, name="Withdraw"),
    path('bank-details/', views.bank_details, name='bank_details'),
    path('upi-details/', views.upi_details_page, name='upi_details_page'),
    path("GameHistory/", views.GameHistory, name="GameHistory"),
    path("logout/", auth_views.LogoutView.as_view(next_page="index"), name="logout"),

    path('place_bet/', views.place_bet, name='place_bet'),
    path('store_game_result/', views.store_game_result, name='store_game_result'),

    path('api/bets/', BetListCreateView.as_view(), name='bet-list-create'),
    path('api/wallets/', WalletListCreateView.as_view(), name='wallet-list-create'),
    path('api/game-results/', GameResultListCreateView.as_view(), name='game-result-list-create'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
