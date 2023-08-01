from djoser.serializers import UserSerializer as BaseUserSerializer
from djoser.serializers import UserCreateSerializer as Base

class UserCreateSerializer(Base):
    class Meta(Base.Meta):
        fields = ['id', 'username', 'password', 'email', 'cargo', 'first_name', 'last_name']

class UserSerializer(BaseUserSerializer):
    class Meta(Base.Meta):
        fields = ['id', 'username','cargo', 'first_name', 'last_name']