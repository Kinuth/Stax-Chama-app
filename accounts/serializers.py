from rest_framework import serializers
from .models import user

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = user
        fields = ('phone', 'password', 'first_name', 'last_name', 'national_id')

    def create(self, validated_data):
        new_user = user.objects.create( 
            phone=validated_data['phone'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            national_id=validated_data.get('national_id'),
        )
        new_user.set_password(validated_data['password'])
        new_user.save()
        return new_user