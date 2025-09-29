from decimal import Decimal
from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpRequest,JsonResponse
from.models import Student,Profile,Account,Transaction,KYCDocument
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q 

# Create your views here.
def loginView(request : HttpRequest) :
    error,message = None, None
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        if not password or len(password) < 8 :
            return render(request,'login.html',{"error":True, "message" : "password is required and must meet minimum to login"})

        user_returned = authenticate(request,username=email,password=password)
        if not user_returned :
            return render(request,'login.html',{"error":True, "message" : "invalid credentials "})
        login(request, user_returned)
        return redirect("client-page")

    return render(request,'login.html',{"error":error, "message":message}) 
    #  HttpResponse('''
    #     <h2>Login Page</h2>
    #     <p>LOGIN PAGE FORMS</p>               

    # '''  )
def signUp(request : HttpRequest):
   error = None
   if request.method == "POST":
       email = request.POST.get("email")
       password1 = request.POST.get("password1")
       password2 = request.POST.get("password2")

       if password1 != password2 or len(password1) < 8 :
           error = 'Ensure both passwords match and password has at least 8 characters'

       else :
            try :
                user_exist = User.objects.filter(username = email).first()
                if user_exist :
                    error = 'User already exist for for this account'
                else :
                    user = User.objects.create_user(username = email,password=password1)
                    # we can generate an account number for the user here
                    account = Account.objects.create( user = user)
                    user.save()
                    account.save()

                    return redirect("client-login")
            except Exception as e :
                error = str(e)        

   return render(request,'signup.html', {"error" : error,}) 

@login_required(login_url='client-login')
def transferPage(request : HttpRequest):
    error = None
    owner_account = Account.objects.get(user= request.user)
    if request.method == "POST":
        reciever_account_number = request.POST.get("account_number")
        amount_to_send = request.POST.get("amount")
        sender_pin = request.POST.get("pin")

        #first check amount is valid then check if the balance is enough
        if not amount_to_send or not amount_to_send.isdigit() :
            return render(request,'transfer.html', {"error": 'Amount to send must be a valid number', "accout" : owner_account})
    
        user_balance = owner_account.balance
        amount_to_decimal = Decimal(amount_to_send)
        #user balance must not be less than amount he or she is to send 
        if user_balance < amount_to_decimal:
            return render(request,'transfer.html', {"error" : 'You have insufficient balance or invalid pin', "account": owner_account})
        
        # check if the user sends in pin
        if not sender_pin or not sender_pin.isdigit() or len (sender_pin) != 4 :
            return render(request, 'transfer.html', {"error": 'you must enter your pin and must all be a 4 digit pin', "account" : owner_account})
        
        # next confirm the user pin 
        is_pin_correct = owner_account.verifyPw(sender_pin)
        if not is_pin_correct :
            return render(request,'transfer.html', {"error" : 'Invalid pin entered!', "account" : owner_account})
        
        #next is for checking the account number of the reciever etc
        if not reciever_account_number or not reciever_account_number.isdigit() or len(reciever_account_number) != 10 :
            return render(request,'transfer.html', {"error" : 'Reciever Account number must be valid or exist and must be a 10 digit number!', "account": owner_account})
        
        try :
            reciever_account = Account.objects.get(account_number = reciever_account_number)
            # increase the reciever balance and decrease the sender balance
            reciever_account.balance += amount_to_decimal
            owner_account.balance -= amount_to_decimal

            owner_account.save()
            reciever_account.save()
            transaction = Transaction.objects.create(from_account = owner_account,to_account = reciever_account, amount = amount_to_decimal, status = 'success',
            transaction_type = 'Transfer')
            transaction.save()
        
            return render(request,'transfer.html', {"success": f'Transfer of NGN{amount_to_send} succesfully sent to {reciever_account.user.username}', 'account': owner_account, "transaction_ref": transaction.ref})
       
        except Account.DoesNotExist:
            return render(request, 'transfer.html', {"error" : f'Account number {reciever_account_number} not found!', "account": owner_account})    
    
   
    return render(request,'transfer.html', {"error": error, "account":   owner_account})

@login_required(login_url='client-login')
def pinPage(request : HttpRequest):
    user_has_pin = False
    account = Account.objects.get(user = request.user)
    if account.pin_hash :
       user_has_pin = True

    if request.method == "POST":
        new_pin = request.POST.get("new_pin")
        confirm_pin = request.POST.get("confirm_pin")

        if not new_pin or new_pin != confirm_pin or len(new_pin) != 4 or not new_pin.isdigit():
            return render(request, 'pin.html', {'user_has_pin' : user_has_pin, "error": "new password must be a 4 digit number and both new password and  confirm password must tally"}) 
    
        if user_has_pin :
            current_pin = request.POST.get ("current_pin")
            if not current_pin or len(current_pin) != 4 or not current_pin.isdigit():
                return render(request,'pin.html', {'user_has_pin' : user_has_pin, "error" : "you must enter your current pin and it must be a 4 digit pin"})
            is_correct = account.verifyPw(current_pin)
            if not is_correct:
                return render(request, 'pin.html', {"user_has_pin" : user_has_pin, "error": "wrong pin entered!"})
            
            account.createPin(new_pin)
            return render(request,'pin.html', {"user_has_pin": True, "success": "Pin updated successfully"})

        #if we doing update we process them all in here
        #if it gets down here this means the user has not set pin 
        # at this stage it means all validation for setting a new pin is good to go
        account.createPin(new_pin)
        return render(request,'pin.html', {"user_has_pin": True, "success": "Pin updated successfully"})    

    return render(request,'pin.html', { 'user_has_pin': user_has_pin })

@login_required(login_url='client-login')
def profilePage(request : HttpRequest):
    return render(request,'profile.html', { })


@login_required(login_url='client-login')
def dashboardPage(request : HttpRequest):
    user = request.user
    account = Account.objects.get_or_create(user=user)
    return render(request,'dashboard.html', {"account": account[0] })

@login_required(login_url='client-login')
def transactionPage(request : HttpRequest) :
    account = Account.objects.get(user=request.user)
    transactions = Transaction.objects.filter(Q(from_account = account) | Q(to_account = account))
    return render(request,'transactions.html', { "transactions": transactions })

@login_required(login_url='client-login')
def searchUser(request : HttpRequest):
   user_to_search = request.GET.get("search")
   if not user_to_search :
       return HttpResponse("<p>Nothing to search</p>")
   
   try:
       user_found = User.objects.get(username = user_to_search)
       return HttpResponse(f'<p> user {user_found.username} found with id{user_found.id}</p>')
   except User.DoesNotExist as e:
       return HttpResponse("<p>User Does not exist</p> ")
   except Exception as e :
       return HttpResponse("Error Occurred ")   
       
@login_required(login_url='client-login')
def logoutPage(request : HttpRequest):
    logout(request)
    return redirect("client-login")
####template represent the ui the user sees when visiting a website
# HttpResponse('''
#       <h2>signup page</h2>
#       <textarea style= "color:blue;"></textarea>
                        

# ''' )


# def cardPurchaseEndpoint(request):
#     description = {
#          "buy_card" : "/card/purchase",
#          "amount": [500,1000,2000,3000],
#          'method' : "POST"
#         }
#     return JsonResponse(
#         data = description
    
#     )

# def getAllProfile(request:HttpRequest) -> JsonResponse:
#     profiles = Profile.objects.filter()
#     data = {}
#     count = 0
#     for profile in profiles :
#         data[count] = {
#             'username' : profile.user.username,
#             'phone' : profile.phone
#         }
#         count += 1

#     return JsonResponse(
#        data = data,
#        safe = False
    
#     )

# @login_required(login_url='client-login')
# def profilePage(request):
#     user : User = request.user
#     try:
#         pass
#     except Profile.DoesNotExist :
#         return render(request,'profiles.html',{"username":None})     
#     return render(request,'profiles.html',{"username":user.username})

