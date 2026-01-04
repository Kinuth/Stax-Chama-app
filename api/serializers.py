from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import User, ChamaGroup, Loan, Contribution

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

class ContributionSerializer(serializers.ModelSerializer):
    # This allows the frontend to show "John Doe" instead of "User ID: 5"
    member_name = serializers.ReadOnlyField(source='member.username')
    group_name = serializers.ReadOnlyField(source='group.name')

    class Meta:
        model = Contribution
        fields = ['id', 'group', 'group_name', 'member', 'member_name', 'amount', 'date']
        # Member is read-only because we set it automatically in the Viewset
        read_only_fields = ['member', 'date']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Contribution amount must be greater than zero.")
        return value

class LoanSerializer(serializers.ModelSerializer):
    total_to_pay = serializers.ReadOnlyField(source='total_repayment')
    class Meta:
        model = Loan
        fields = ['id', 'borrower', 'group', 'amount', 'interest_rate', 'status', 'total_to_pay']
        read_only_fields = ['borrower', 'status']