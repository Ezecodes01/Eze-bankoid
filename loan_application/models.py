# loan_application/models.py
from django.db import models

class LoanApplication(models.Model):
    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    ssn = models.CharField(max_length=20)
    dob = models.DateField()
    address = models.TextField()

    # Income Information
    status = models.CharField(max_length=50)
    income = models.DecimalField(max_digits=10, decimal_places=2)
    employer_name = models.CharField(max_length=255, blank=True, null=True)
    employment_length = models.IntegerField()
    job_title = models.CharField(max_length=255, blank=True, null=True)

    # Loan Requirements
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2)
    loan_purpose = models.CharField(max_length=255)
    loan_term = models.IntegerField()

    # Document Uploads
    id_proof = models.FileField(upload_to='documents/id_proofs/')
    income_proof = models.FileField(upload_to='documents/income_proofs/')
    bank_statement = models.FileField(upload_to='documents/bank_statements/')

    submission_date = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"Application from {self.first_name} {self.last_name}"