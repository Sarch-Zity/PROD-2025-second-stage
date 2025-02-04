from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from users.authentication import is_customer
from rest_framework.permissions import IsAuthenticated
from .serializers import CustomUserSerializer, BusinessSerializer, CustomerSerializer, CustomerTargetSerializer, ProfileCustomerSerializer, PachProfileSerializer, UserLoginSerializer
from .models import CustomUser, Business, Customer, CustomerTarget
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import authenticate
from django.core.cache import cache
from uuid import uuid4
from .authentication import is_customer
from .validators import password_validator

ERROR400 = Response({"status": "error", "message": "Ошибка в данных запроса."}, status=400)
ERROR409 = Response({"status": "error", "message": "Такой email уже зарегистрирован."}, status=409)
ERROR401 = Response({"status": "error", "message": "Неверный email или пароль."}, status=401)

def get_token(user):
    token = AccessToken.for_user(user)
    token["userid"] = user.id
    token["jti"] = str(uuid4())
    cache.set(user.id, token["jti"], timeout=82800)
    return token

@api_view(["POST"])
def business_sign_up(request):
    serializer = CustomUserSerializer(data = request.data)
    serializer2 = BusinessSerializer(data = request.data)

    if serializer.is_valid() and serializer2.is_valid():
        user = CustomUser(is_business = True)
        user.set_password(serializer.validated_data["password"])
        user.save()

        business = Business(**serializer2.validated_data, user = user)
        business.save()

        token = get_token(user)
        return Response({"token": str(token), "company_id": business.uuid}, status=200)
    else:
        try:
            if Business.objects.filter(email = request.data["email"]).exists():
                return ERROR409
        except:
            pass
        return ERROR400

@api_view(["POST"])
def business_sign_in(request):
    serializer = UserLoginSerializer(data = request.data)

    if serializer.is_valid():
        login = Business.objects.filter(email = serializer.validated_data["email"])
        if not login.exists():
            return ERROR401
        
        id = login.first().user.id
        user = authenticate(id = id, password = serializer.validated_data["password"])
        if user == None:
            return ERROR401
        
        token = get_token(user)
        return Response({"token": str(token)}, status=200)
    
    else:
        return ERROR400
    
@api_view(["POST"])
def customer_sign_up(request):
    serializer = CustomUserSerializer(data = request.data)
    serializer2 = CustomerSerializer(data = request.data)

    if serializer.is_valid() and serializer2.is_valid():
        if "avatar_url" in request.data and request.data["avatar_url"] == "": return ERROR400
        user = CustomUser(is_business = False)
        user.set_password(serializer.validated_data["password"])
        user.save()

        other = serializer2.validated_data.pop("other")
        serializer3 = CustomerTargetSerializer(data = other)

        customer = Customer(user = user, **serializer2.validated_data)
        customer.save()

        if serializer3.is_valid():
            target = CustomerTarget(customer = customer, **serializer3.validated_data)
            target.save()
        else:
            user.delete()
            return ERROR400

        token = get_token(user)
        return Response({"token": str(token)}, status=200)
    else:
        try:
            if Customer.objects.filter(email = request.data["email"]).exists():
                return ERROR409
        except:
            pass
        return ERROR400

@api_view(["POST"])
def customer_sign_in(request):
    serializer = UserLoginSerializer(data = request.data)

    if serializer.is_valid():
        login = Customer.objects.filter(email = serializer.validated_data["email"])
        if not login.exists():
            return ERROR401
        
        id = login.first().user.id
        user = authenticate(id = id, password = serializer.validated_data["password"])
        if user == None:
            return ERROR401
        
        token = get_token(user)
        return Response({"token": str(token)}, status=200)
    
    else:
        return ERROR400

@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
@is_customer
def customer_profile(request):
    if request.method == "PATCH":
        if "name" in request.data and request.data["name"] == None: request.data.pop("name")
        if "surname" in request.data and request.data["surname"] == None: request.data.pop("surname")
        if "password" in request.data and request.data["password"] == None: request.data.pop("password")
        
        serializer1 = PachProfileSerializer(request.user.customer, data = request.data)

        if not serializer1.is_valid(): return ERROR400
        serializer1.save()
        
        if "password" in request.data:
            serializer2 = CustomUserSerializer(request.user, data = request.data)

            if not serializer2.is_valid(): return ERROR400
            request.user.set_password(serializer2.validated_data["password"])
            request.user.save()
        
        # return Response(serializer.errors, status=400)        

    serializer = ProfileCustomerSerializer(request.user.customer)
    output = serializer.data
    if output["avatar_url"] in [None, ""]:
        output.pop("avatar_url")
    return Response(output, status=200)