from rest_framework import serializers
from accounts.models import User, Config
from main.utils import make_absolute_uri


class ConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = Config
        fields = ('key', 'value')
        read_only_fields = ('key', 'value')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk', 'email', 'name', 'is_adult', 'age', 'sex', 'profile_image',
                  'phone_number', 'is_active')
        extra_kwargs = {'password': {'write_only': True}, 'phone_number': {'write_only': True}}

    def to_representation(self, obj):
        res = super().to_representation(obj)
        if obj.profile_image:
            res['profile_image'] = make_absolute_uri(obj.profile_image.url)
        return res

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = self.Meta.model(**validated_data)
        if password is not None:
            user.set_password(password)
        user.save()
        return user

    def update(self, user, validated_data):
        for attr, value in validated_data.items():
            if attr == 'password':
                user.set_password(value)
            else:
                setattr(user, attr, value)
        user.save()
        return user


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(min_length=4)
    new_password_confirm = serializers.CharField(min_length=4)

    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError('Password confirm doest not match')
        return data


class ChangeProfileSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    date_of_birth = serializers.DateField(required=False)
    icon = serializers.CharField(required=False, allow_null=True)
    profile_image = serializers.ImageField(required=False, allow_null=True)
    sex = serializers.CharField(required=False)


class DeviceRegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50)
    birth = serializers.DateField()
    device_type = serializers.CharField(max_length=10)
    push_token = serializers.CharField(max_length=512, required=False, allow_null=True, allow_blank=True)


class DeviceLoginSerializer(serializers.Serializer):
    login_secret = serializers.CharField(max_length=20)
    push_token = serializers.CharField(max_length=512, required=False, allow_null=True, allow_blank=True)


class DeviceLogoutSerializer(serializers.Serializer):
    login_secret = serializers.CharField(max_length=20)
