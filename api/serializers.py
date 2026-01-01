from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import User, ChamaGroup, Loan

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['date_joined']


class ChamaGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChamaGroup
        fields = '__all__'  # or list specific fields
        read_only_fields = ['created_by']

class LoanSerializer(serializers.ModelSerializer):
    total_to_pay = serializers.ReadOnlyField(source='total_repayment')
    class Meta:
        model = Loan
        fields = ['id', 'borrower', 'group', 'amount', 'interest_rate', 'status', 'total_to_pay']