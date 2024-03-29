from django.shortcuts import render, redirect
from django.views import View

# Login Authontication
from .forms import UserregistrationForm
from django.contrib import messages
from .models import UserProfile
from .forms import ProfileSettingsForm
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.contrib import messages
from datetime import datetime
from .models import DepositMessage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from Authentication.views import signup, signin, signout, activate, forgot_password, reset_password, password_reset_sucess


# Create your views here.
def index(request):
    return render(request, "DiceApp/index.html")

def PracticeGame(request):
    return render(request, "DiceApp/practicegamecode.html")

def About(request):
    return render(request, "DiceApp/about.html")

def How_to_play(request):
    return render(request, "DiceApp/how-to-play.html")

# Login Authontication
def login(request):
    return signin(request)

def signup_view(request):
    return signup(request)

def logout(request):
    return signout(request)

def account_activate(request):
    return activate(request)

def forgot_password(request):
    return forgot_password(request)

def reset_password(request):
    return reset_password(request)

def reset_password_success(request):
    return reset_password_success(request)

# User-Profile section

class ProfileView(View):
    template_name = "DiceApp/1.html"

    def get(self, request):
        # Check if the user is authenticated
        if request.user.is_authenticated:
            # Access the logged-in user
            
            username = request.user.username
            return render(request, self.template_name, {"username": username})

        else:
            return render(request, "DiceApp/not_authenticated.html", locals())


# user-profile view


class User_profile(View):
    template_name = "DiceApp/User-Profile.html"
    
    def get(self, request):
        # Check if the user is authenticated
        if request.user.is_authenticated:
            # Access the logged-in user's information
            user = request.user
            username = user.username
            # full_name= user.full_name
            email = user.email
            profile_picture = "https://via.placeholder.com/150"
            country = "India"

            joined_date = user.date_joined.strftime("%B %d, %Y")
            last_login = user.last_login.strftime("%B %d, %Y")

            return render(
                request,
                self.template_name,
                {
                    "username": username,
                    # 'full_name':full_name,
                    "email": email,
                    "profile_picture": profile_picture,
                    "country": country,
                    "joined_date": joined_date,
                    "last_login": last_login,
                },
            )
        else:
            return render(request, "DiceApp/not_authenticated.html", locals())
# For User Profile-setting

class ProfileSettingsView(View):
    template_name = "DiceApp/profile-setting.html"

    def get(self, request):
        if request.user.is_authenticated:
            user_profile = UserProfile.objects.get(user=request.user)
            form = ProfileSettingsForm(instance=user_profile)
            return render(request, self.template_name, {"form": form})
        else:
            return render(request, "DiceApp/not_authenticated.html", locals())

    def post(self, request):
        if request.user.is_authenticated:
            user_profile = UserProfile.objects.get(user=request.user)
            form = ProfileSettingsForm(
                request.POST, request.FILES, instance=user_profile
            )

            if form.is_valid():
                form.save()
                return redirect("user_profile")

            return render(request, self.template_name, {"form": form})
        else:
            return render(request, "DiceApp/not_authenticated.html", locals())


# other things

from decimal import Decimal
from django.shortcuts import render

def Mybalance(request, balance=None):
    if request.method == "GET":
        print("Website reloaded")
        balance_decimal = Decimal(balance) if balance else Decimal("0.00")
        return render(request, "DiceApp/my-balance.html", {"balance": balance_decimal})


# Latest Balance
from django.shortcuts import render
from .models import Wallet

def check_balance(request):
    user = request.user

    # Logic to retrieve the latest balance from the database
    try:
        wallet = Wallet.objects.get(user=user)
        latest_balance = wallet.balance
    except Wallet.DoesNotExist:
        latest_balance = 0.00

    return render(
        request,
        "DiceApp/my-balance.html",
        {"latest_balance": latest_balance}
    )


def Profile_settings(request):
    return render(request, "DiceApp/profile-setting.html")


def Inbox(request):
    deposit_messages = DepositMessage.objects.all()
    return render(request, 'DiceApp/inbox.html', {'deposit_messages': deposit_messages})

# Deposit sucess
from django.contrib.auth.decorators import login_required
@login_required
def view_all_deposits(request):
    user = request.user
    deposit_messages = DepositMessage.objects.filter(user=user).order_by('-date')
    
    # Configure pagination
    paginator = Paginator(deposit_messages, 5)
    page = request.GET.get('page')

    try:
        deposit_messages = paginator.page(page)
    except PageNotAnInteger:
        deposit_messages = paginator.page(1)
    except EmptyPage:
        deposit_messages = paginator.page(paginator.num_pages)

    return render(request, 'DiceApp/all_deposits.html', {'deposit_messages': deposit_messages})

def GameHistory(request):
    return render(request, "DiceApp/game-history.html")

def success_page(request, balance=None):
    return render(request, "DiceApp/success.html", {'balance': balance})


# Game logic


class PlayGameView(View):
    def post(self, request):
        if request.user.is_authenticated:
            try:
                user_profile = UserProfile.objects.get(user=request.user)
            except ObjectDoesNotExist:
                return JsonResponse(
                    {"success": False, "message": "User profile not found"}
                )

            selected_image = request.POST.get("selected_image", None)
            bet_amount = int(request.POST.get("bet_amount", 0))

            # Simulate the dice roll (replace this with your actual game logic)
            result_images = ["lion", "horse", "monkey", "panda", "deer", "elephant"]
            result = [
                selected_image,
                result_images[1],
                result_images[2],
                selected_image,
                result_images[4],
                result_images[5],
            ]

            # Count occurrences of the selected image in the result
            image_count = result.count(selected_image)

            # Calculate the total amount based on occurrences
            total_amount = bet_amount * (2 if image_count > 1 else -1)

            # Update user balance
            user_profile.balance += total_amount
            user_profile.save()

            # Display a message based on the result
            if total_amount > 0:
                messages.success(
                    request, f"Congratulations! You won {total_amount} Rs."
                )
            else:
                messages.warning(request, f"Oops! You lost {abs(total_amount)} Rs.")

            return JsonResponse(
                {"success": True, "message": "Game result processed successfully"}
            )
        else:
            return JsonResponse({"success": False, "message": "User not authenticated"})


from django.shortcuts import render
from decimal import Decimal


def payment_view(request, balance=None):
    if request.method == "GET":
        print("Website reloaded")
        balance_decimal = Decimal(balance) if balance else Decimal("0.00")
        return render(request, "DiceApp/Add_cash.html", {"balance": balance_decimal})


from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from instamojo_wrapper import Instamojo
from .models import Wallet
from decimal import Decimal
import razorpay

@login_required
def initiate_payment(request):
    user = request.user
    wallet, created = Wallet.objects.get_or_create(user=user)

    if request.method == "POST":
        amount = request.POST.get("amount")

        # Validate the amount if needed
        if not amount or not amount.isdigit():
            return JsonResponse({"error": "Invalid amount"})

        api = Instamojo(
            api_key=settings.API_KEY,
            auth_token=settings.AUTH_TOKEN,
            endpoint="https://test.instamojo.com/api/1.1/",
        )

        try:
            response = api.payment_request_create(
                amount=amount,
                purpose="Wallet Recharge",
                send_email=True,
                email=user.email,
                redirect_url="http://127.0.0.1:8000/success/",  # Redirect URL after successful payment
            )

            # Save payment request ID in the wallet model for reference
            wallet.payment_request_id = response.get("payment_request").get("id")
            wallet.save()

            # Access the payment URL based on the actual structure
            payment_url = response.get("payment_request").get("longurl")

            if payment_url:
                # Redirect the user to the payment URL
                return redirect(payment_url)
            else:
                return JsonResponse({"error": "Invalid response from Instamojo"})

        except Exception as e:
            return JsonResponse({"error": str(e)})

    return render(request, "DiceApp/Add_cash.html")


# views.py

from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import JsonResponse
from decimal import Decimal
from datetime import datetime
from django.conf import settings
from instamojo_wrapper import Instamojo
from .models import Wallet

@login_required
def success(request):
    user = request.user

    # Check if the user has a wallet
    try:
        wallet = Wallet.objects.get(user=user)
    except Wallet.DoesNotExist:
        return JsonResponse({"error": "Wallet not found for the user"})

    # Get payment request details
    payment_request_id = request.GET.get("payment_request_id")
    api = Instamojo(
        api_key=settings.API_KEY,
        auth_token=settings.AUTH_TOKEN,
        endpoint="https://test.instamojo.com/api/1.1/",
    )
    try:
        payment_request = api.payment_request_status(payment_request_id)

        # Check if 'status' key is present in the response
        if (
            "payment_request" in payment_request
            and "status" in payment_request["payment_request"]
        ):
            if payment_request["payment_request"]["status"] == "Completed":
                # Update wallet balance
                deposited_amount = Decimal(payment_request["payment_request"]["amount"])
                wallet.balance += deposited_amount
                wallet.save()

                # Save deposit message to the model
                DepositMessage.objects.create(user=request.user, message=f'Deposit of ₹{deposited_amount} was successful on {datetime.now()}.')
                
                # Display success message
                messages.success(
                    request,
                    f'Deposit of ₹{deposited_amount} was successful on {datetime.now()}.'
                )

                # Redirect to the success page with the updated balance
                return redirect("success_page", balance=wallet.balance)
            else:
                return JsonResponse(
                    {
                        "error": f"Payment status is not 'Completed'. Actual status: {payment_request['payment_request']['status']}"
                    }
                )
        else:
            return JsonResponse(
                {"error": "Unexpected response structure from Instamojo"}
            )

    except Exception as e:
        return JsonResponse({"error": str(e)})
    
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Wallet
from collections import Counter

import logging
from collections import Counter
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Wallet

# Add logging configuration at the beginning of your views.py
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@login_required
def place_bet(request):
    if request.method == 'POST':
        selected_dice = request.POST.get('selected_dice')

        # Print the entire POST data for debugging
        logger.debug("POST data: %s", request.POST)

        # Check if 'selected_amount' is present in the POST data
        if 'selected_amount' not in request.POST:
            logger.error("selected_amount is not present in the POST data")
            return JsonResponse({'status': 'error', 'message': 'Invalid amount'})

        selected_amount = request.POST['selected_amount']

        try:
            selected_amount = int(selected_amount)
        except (TypeError, ValueError):
            logger.error("Invalid selected_amount: %s", selected_amount)
            return JsonResponse({'status': 'error', 'message': 'Invalid amount'})
        # Deduct the bet amount from the user's wallet
        user_wallet = Wallet.objects.get(user=request.user)

        # Check if user_wallet is not None before accessing its balance
        if user_wallet and user_wallet.balance >= selected_amount:
            user_wallet.balance -= selected_amount
            user_wallet.save()

            # Add your additional logic here, like updating the game state or saving the bet in the database.

            return JsonResponse({'status': 'success', 'message': 'Bet placed successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Insufficient funds'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

import json
from django.http import JsonResponse

@login_required
def store_game_result(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)
            
            # Ensure 'bet_amount' is present in the JSON data
            if 'bet_amount' not in data:
                return JsonResponse({'status': 'error', 'message': 'No bet amount provided'})

            result_images = data.get('result_images', [])
            bet_amount = int(data['bet_amount'])

            # Calculate the won amount based on the result images and bet amount
            won_amount = calculate_won_amount(result_images, bet_amount)

            # Update the user's wallet if they won
            if won_amount > 0:
                user_wallet = Wallet.objects.get(user=request.user)
                user_wallet.balance += won_amount
                user_wallet.save()

            return JsonResponse({'status': 'success', 'message': 'Game result stored successfully'})
        except json.JSONDecodeError as e:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


def calculate_won_amount(result_images, bet_amount):
    # Count occurrences of each image in the result
    image_counts = Counter(result_images)

    # Initialize won_amount to zero
    won_amount = 0

    # Check for winning conditions and accumulate won amount
    for count in image_counts.values():
        if count == 2:
            won_amount += bet_amount * 2
        elif count == 3:
            won_amount += bet_amount * 3
        elif count == 4:
            won_amount += bet_amount * 4
        elif count == 5:
            won_amount += bet_amount * 5
        elif count == 6:
            won_amount += bet_amount * 6
        # Add more conditions for higher counts if needed

    return won_amount

# views.py

from rest_framework import generics
from rest_framework.response import Response
from .models import Bet, GameResult, Wallet
from .serializers import BetSerializer, GameResultSerializer, WalletSerializer
from django.http import JsonResponse
import random

class BetListCreateView(generics.ListCreateAPIView):
    queryset = Bet.objects.all()
    serializer_class = BetSerializer

    def create(self, request, *args, **kwargs):
        selected_image = request.data.get('selected_image')
        bet_amount = request.data.get('bet_amount')

        # Display a confirmation dialog
        confirm_bet = request.data.get('confirm_bet')

        if confirm_bet == 'true':
            user = request.user

            # Check if the user has sufficient balance in the wallet
            wallet = Wallet.objects.get(user=user)
            if wallet.balance < float(bet_amount):
                return JsonResponse({'result': 'failed', 'message': 'Insufficient balance in the wallet'})

            # Deduct the bet amount from the wallet
            wallet.balance -= float(bet_amount)
            wallet.save()

            # Save the user bet
            bet = Bet.objects.create(
                user=user,
                selected_image=selected_image,
                bet_amount=bet_amount
            )

            # Simulate dice roll and determine the result
            symbols = ['lion', 'horse', 'monkey', 'panda', 'deer', 'elephant']
            result = 'won' if selected_image in random.sample(symbols * 2, 2) else 'lost'
            won_amount = float(bet_amount) * 2 if result == 'won' else 0

            # Update the bet with the result and won_amount
            bet.result = result
            bet.won_amount = won_amount
            bet.save()

            # Save the game result
            GameResult.objects.create(
                user=user,
                symbol=selected_image,
                won_amount=won_amount
            )

            # Update the wallet based on the game result
            wallet.balance += won_amount
            wallet.save()

            return JsonResponse({'result': result, 'won_amount': won_amount, 'wallet_balance': wallet.balance})

        else:
            return JsonResponse({'result': 'canceled'})


from rest_framework import generics
from .models import Wallet
from .serializers import WalletSerializer

class WalletListCreateView(generics.ListCreateAPIView):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer


from rest_framework import generics
from .models import GameResult
from .serializers import GameResultSerializer

class GameResultListCreateView(generics.ListCreateAPIView):
    queryset = GameResult.objects.all()
    serializer_class = GameResultSerializer
    

# For withdraw

def Withdraw(request):
    user_wallet = Wallet.objects.get(user=request.user)
    latest_balance=user_wallet.balance
    return render(request, 'DiceApp/withdraw.html', {'latest_balance': latest_balance})

def bank_details(request):
    return render(request, 'DiceApp/bank-details.html')

def upi_details_page(request):
    return render(request, 'DiceApp/upi_details_page.html')

# Razorpay Payment integration start


from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
from .models import Wallet, DepositMessage
from decimal import Decimal
from datetime import datetime
import razorpay

@login_required
def initiate_razorpay_payment(request):
    if request.method == "POST":
        user = request.user
        wallet, created = Wallet.objects.get_or_create(user=user)
        amount = request.POST.get("amount")

        # Validate the amount if needed
        if not amount or not amount.isdigit():
            return JsonResponse({"error": "Invalid amount"})

        # Initialize Razorpay client with API key and secret key
        client = razorpay.Client(auth=(settings.rzp_test_AigyCc6s5GehQ0, settings.W5qsSkr2pZAcBoTpdoTKMlfd))

        try:
            # Create Razorpay order
            order = client.order.create({
                'amount': int(amount) * 100,  # Amount should be in paisa
                'currency': 'INR',
                'payment_capture': 1  # Auto capture payment
            })

            # Save order ID in session for reference during success callback
            request.session['razorpay_order_id'] = order['id']

            return JsonResponse({"order_id": order['id']})

        except Exception as e:
            return JsonResponse({"error": str(e)})

    return JsonResponse({"error": "Method not allowed"})


@login_required
def razorpay_callback(request):
    user = request.user

    # Check if the Razorpay order ID is present in the session
    if 'razorpay_order_id' in request.session:
        order_id = request.session.pop('razorpay_order_id')
    else:
        return JsonResponse({"error": "Razorpay order ID not found in session"})

    # Fetch Razorpay order details using the order ID
    client = razorpay.Client(auth=(settings.rzp_test_AigyCc6s5GehQ0, settings.W5qsSkr2pZAcBoTpdoTKMlfd))
    try:
        order = client.order.fetch(order_id)

        # Check if the payment is successful
        if order.get('status') == 'paid':
            # Update wallet balance
            wallet, created = Wallet.objects.get_or_create(user=user)
            deposited_amount = Decimal(order['amount']) / 100  # Convert amount from paisa to rupees
            wallet.balance += deposited_amount
            wallet.save()

            # Save deposit message to the model
            DepositMessage.objects.create(user=user, message=f'Deposit of ₹{deposited_amount} was successful on {datetime.now()}.')

            # Display success message
            messages.success(request, f'Deposit of ₹{deposited_amount} was successful on {datetime.now()}.')

            # Redirect to the success page with the updated balance
            return redirect("success_page", balance=wallet.balance)

        else:
            return JsonResponse({"error": "Payment not successful"})

    except Exception as e:
        return JsonResponse({"error": str(e)})

# For Withdraw Amount

# views.py

from django.http import JsonResponse
import razorpay

@login_required
def withdraw(request):
    client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

    if request.method == 'POST':
        amount = request.POST.get('amount')
        recipient = request.POST.get('recipient')

        # Create a Razorpay payout
        payout_data = {
            'account_number': recipient.account_number,
            'fund_account_id': 'YOUR_RAZORPAY_FUND_ACCOUNT_ID',
            'amount': amount * 100,  # Amount should be in paise
            'currency': 'INR',
            'mode': 'NEFT',
            'purpose': 'refund',
            'queue_if_low_balance': True
        }

        try:
            payout = client.payouts.create(data=payout_data)
            return JsonResponse({'success': True, 'payout': payout})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


