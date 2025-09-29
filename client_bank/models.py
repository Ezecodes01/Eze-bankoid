from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from random import randint 
from django.contrib.auth.hashers import make_password, check_password

def generate_account_number():
    """
    a simple function to use to generate our  account number ...
    """
    return str(randint(1000000000, 9999999999))

def generateTranscationRef():
   '''
   
    a simple function to use to generate our  account number ...
   '''
   return "TRS-" + str(randint(1000000000000,9999999999000))


# Create your models here.
class  Student(models.Model) :
    name = models.CharField(max_length=55)
    age = models.PositiveIntegerField(max_length=3)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True, null=True)
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    kyc_status = models.CharField(max_length=20, choices=[
    ('NOT_SUBMITTED','Not submitted'),
    ('PENDING','Pending'),
    ('VERIFIED','Verified'),
    ('REJECTED','Rejected')
    ], default='NOT_SUBMITTED')
    def __str__(self):
     return self.user.username


class Account(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, 
    on_delete=models.CASCADE)
    account_number = models.CharField(max_length=10, unique=True, default=generate_account_number)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(1000))
    pin_hash = models.CharField(max_length=128, blank=True) # store hashed 
    created_at = models.DateTimeField(auto_now_add=True)

    def createPin(self,pin : str ):
        '''
         this class methods accept a 4 digit pin
         and hashes it        
        '''
        self.pin_hash = make_password(pin)
        self.save()

    def verifyPw(self,pin) -> bool :
        if not self.pin_hash :
           return False
        return check_password(pin,self.pin_hash)    
    


    def __str__(self):
     return f"{self.user.username} — {self.account_number}"

class Transaction(models.Model):
    TRANSACTION_TYPE = [('TRANSFER','Transfer'), ('DEPOSIT','Deposit'), 
    ('WITHDRAW','Withdraw')]
    ref = models.CharField(max_length=64, unique=True, default=generateTranscationRef )
    from_account = models.ForeignKey(Account, on_delete=models.SET_NULL, 
null=True, related_name='outgoing')
    to_account = models.ForeignKey(Account, on_delete=models.SET_NULL, 
null=True, related_name='incoming')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, 
choices=[('PENDING','Pending'),('SUCCESS','Success'),('FAILED','Failed')], 
default='PENDING')
    transaction_type = models.CharField(max_length=20, 
choices=TRANSACTION_TYPE)
    
    created_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
     return f"{self.ref} — {self.amount}"

class KYCDocument(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    document = models.FileField(upload_to='kyc/')
    doc_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, 
blank=True, on_delete=models.SET_NULL, related_name='+')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True, null=True)
    

