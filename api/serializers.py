from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import User, ChamaGroup, Loan

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'phone_number', 'national_id')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            phone_number=validated_data.get('phone_number', ''),
            national_id=validated_data.get('national_id', '')
        )
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['date_joined']


class ChamaGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChamaGroup
        fields = ['id', 'name', 'balance', 'chairman']
        read_only_fields = ['balance', 'chairman'] # User only sends 'name'

class LoanSerializer(serializers.ModelSerializer):
    total_to_pay = serializers.ReadOnlyField(source='total_repayment')
    class Meta:
        model = Loan
        fields = ['id', 'borrower', 'group', 'amount', 'interest_rate', 'status', 'total_to_pay']