from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "phone", "role", "bio", "avatar_url", "date_joined"]
        read_only_fields = ["id", "role", "date_joined"]


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["username", "email", "phone", "password", "role"]

    def validate(self, attrs):
        if not attrs.get("email") and not attrs.get("phone"):
            raise serializers.ValidationError("邮箱或手机号至少填写一个。")
        return attrs

    def create(self, validated_data):
        username = validated_data.get("username")
        if not username:
            seed = validated_data.get("email") or validated_data.get("phone") or "reader"
            username = seed.split("@")[0]
            base = username
            index = 1
            while User.objects.filter(username=username).exists():
                index += 1
                username = f"{base}{index}"
            validated_data["username"] = username

        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    account = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        account = attrs["account"]
        password = attrs["password"]

        if "@" in account:
            user = User.objects.filter(email=account).first()
        elif account.isdigit() or account.startswith("+"):
            user = User.objects.filter(phone=account).first()
        else:
            user = User.objects.filter(username=account).first()

        if not user or not user.check_password(password):
            raise serializers.ValidationError("账号或密码错误。")

        if not user.is_active:
            raise serializers.ValidationError("账号已被禁用。")

        attrs["user"] = user
        return attrs

    @staticmethod
    def build_token_payload(user):
        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserProfileSerializer(user).data,
        }
