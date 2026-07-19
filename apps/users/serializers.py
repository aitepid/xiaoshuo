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
        email = attrs.get("email", "").strip()
        phone = attrs.get("phone", "").strip()
        
        if not email and not phone:
            raise serializers.ValidationError({
                "email": "邮箱或手机号至少填写一个。",
                "phone": "邮箱或手机号至少填写一个。"
            })
        
        # 检查邮箱是否已存在
        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError({
                "email": "该邮箱已被注册。"
            })
        
        # 检查手机号是否已存在
        if phone and User.objects.filter(phone=phone).exists():
            raise serializers.ValidationError({
                "phone": "该手机号已被注册。"
            })
        
        return attrs

    def create(self, validated_data):
        username = validated_data.get("username", "").strip()
        if not username:
            seed = validated_data.get("email") or validated_data.get("phone") or "user"
            username = seed.split("@")[0]
            base = username
            index = 1
            while User.objects.filter(username=username).exists():
                index += 1
                username = f"{base}{index}"
            validated_data["username"] = username

        # 检查用户名是否已存在
        if User.objects.filter(username=validated_data["username"]).exists():
            raise serializers.ValidationError({
                "username": "该用户名已被注册。"
            })

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
