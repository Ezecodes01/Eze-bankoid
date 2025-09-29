# loan_application/views.py
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import LoanApplication
from datetime import datetime

@csrf_exempt
def submit_application(request):
    if request.method == 'POST':
        try:
            # Accessing data from the FormData object
            first_name = request.POST.get('firstName')
            last_name = request.POST.get('lastName')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            ssn = request.POST.get('ssn')
            dob_str = request.POST.get('dob')
            address = request.POST.get('address')
            
            # Income data
            status = request.POST.get('status')
            income = request.POST.get('income')
            employer_name = request.POST.get('employerName')
            employment_length = request.POST.get('employmentLength')
            job_title = request.POST.get('jobTitle')

            # Loan data
            loan_amount = request.POST.get('loanAmount')
            loan_purpose = request.POST.get('loanPurpose')
            loan_term = request.POST.get('loanTerm')

            # Documents
            id_proof_file = request.FILES.get('id_proof')
            income_proof_file = request.FILES.get('income_proof')
            bank_statement_file = request.FILES.get('bank_statement')

            # Basic validation
            if not all([first_name, last_name, email, phone, ssn, dob_str, address, status, income, loan_amount, loan_purpose, loan_term, id_proof_file, income_proof_file, bank_statement_file]):
                return JsonResponse({'error': 'Missing required fields or files.'}, status=400)
            
            # Convert string dates and numbers to their correct types
            try:
                dob_date = datetime.strptime(dob_str, '%Y-%m-%d').date()
                income = float(income)
                employment_length = int(employment_length)
                loan_amount = float(loan_amount)
                loan_term = int(loan_term)
            except (ValueError, TypeError):
                return JsonResponse({'error': 'Invalid data format.'}, status=400)

            # Create and save the new LoanApplication instance
            application = LoanApplication.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                ssn=ssn,
                dob=dob_date,
                address=address,
                status=status,
                income=income,
                employer_name=employer_name,
                employment_length=employment_length,
                job_title=job_title,
                loan_amount=loan_amount,
                loan_purpose=loan_purpose,
                loan_term=loan_term,
                id_proof=id_proof_file,
                income_proof=income_proof_file,
                bank_statement=bank_statement_file,
            )

            return JsonResponse({'message': 'Application submitted successfully!', 'application_id': application.id}, status=201)
        
        except Exception as e:
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Invalid request method.'}, status=405)