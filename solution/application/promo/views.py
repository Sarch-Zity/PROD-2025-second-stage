from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from users.authentication import is_business, is_customer
from rest_framework.permissions import IsAuthenticated
from .serializers import PromoSerializer, TargetSerializer, PaginatorBusinessSerializer, PromoListSerializer, UpdatePromoSerializer, PaginatorCustomerSerializer, PromoListForCustomerSerializer
from .models import Promo, Target
from django.db.models import F, Q
from functools import reduce
import datetime
from django.db.models import Func, Count
from django.db.models import IntegerField
import requests
from django.conf import settings
from django.core.cache import cache

ERROR400 = Response({"status": "error", "message": "Ошибка в данных запроса."}, status=400)
ERROR403 = Response({"status": "error", "message": "Вы не можете использовать этот промокод."}, status=403)

def antifraud_check(request, promo):
    if not cache.get(request.user.customer.email):
        antifraud = requests.post(url="http://" + settings.ANTIFRAUD_ADDRESS + "/api/validate", json={"user_email": request.user.customer.email, "promo_id": str(promo.promo_id)}, headers={"Content-Type": "application/json"})
        if antifraud.status_code != 200: antifraud = requests.post(url="http://" + settings.ANTIFRAUD_ADDRESS + "/api/validate", json={"user_email": request.user.customer.email, "promo_id": str(promo.promo_id)}, headers={"Content-Type": "application/json"})
        if antifraud.status_code != 200: return False
        if antifraud.json()["ok"] == False: return False
        if "cache_until" in antifraud.json():
            cache.set(request.user.customer.email, str(promo.promo_id), ((datetime.datetime.strptime(antifraud.json()["cache_until"], "%Y-%m-%dT%H:%M:%S.%f") + datetime.timedelta(hours=3)) - datetime.datetime.now()).seconds)
    return True

def check_request(request, serializer):
    sort_by = serializer.validated_data["sort_by"]
    if sort_by not in ["active_from", "active_until", "created_at"]:
        return False
    countries = dict(request.GET).get("country")
    x = list()
    if countries:
        countries = [i for j in countries for i in j.split(",")]
        for i in countries:
            if len(i) != 2 or any(char.isdigit() for char in i):
                return False
    return True

def edit_promo_output(output):
    for i in range(len(output)):
        if output[i]["mode"] == "COMMON": output[i].pop("promo_unique")
        else: output[i].pop("promo_common")
        if output[i]["active_from"] == None: output[i].pop("active_from")
        if output[i]["active_until"] == None: output[i].pop("active_until")
        if output[i]["image_url"] == None or output[i]["image_url"] == "": output[i].pop("image_url")
    return output

def format_customers_feed(output, user):
    for i in range(len(output)):
        output[i]["is_activated_by_user"] = Promo.objects.filter(promo_id = output[i]["promo_id"]).filter(used_count__contains = user.id).exists()
        output[i]["is_liked_by_user"] = Promo.objects.filter(promo_id = output[i]["promo_id"]).filter(like_count = user).exists()
        if not output[i]["image_url"]: output[i].pop("image_url")
    return output

# Create your views here.
@api_view(["POST", "GET"])
@permission_classes([IsAuthenticated])
@is_business
def get_and_create_promo(request):
    if request.method == "POST":
        serializer = PromoSerializer(data = request.data)

        if serializer.is_valid():
            if serializer.validated_data.get("active_from") and serializer.validated_data.get("active_until"):
                if serializer.validated_data["active_from"] > serializer.validated_data["active_until"]: return ERROR400
            target = serializer.validated_data.pop("target")
            if (serializer.validated_data["mode"] == "COMMON" and (serializer.validated_data.get("promo_common") == None or serializer.validated_data.get("promo_unique") != None)) or (serializer.validated_data["mode"] == "UNIQUE" and (serializer.validated_data.get("promo_unique") == None or serializer.validated_data.get("max_count") != 1 or serializer.validated_data.get("promo_common"))):
                return ERROR400
            promo = Promo(user = request.user, **serializer.validated_data)
            promo.available_promo_unique = promo.promo_unique
            promo.save()
            serializer2 = TargetSerializer(data = target)
            if serializer2.is_valid():
                if serializer2.validated_data.get("age_from") and serializer2.validated_data.get("age_until"):
                    if serializer2.validated_data["age_from"] > serializer2.validated_data["age_until"]:
                        promo.delete()
                        return ERROR400
                target = Target(promo = promo, **serializer2.validated_data)
                target.save()
            else:
                promo.delete()
                return ERROR400
            return Response({"id": promo.promo_id}, status=201)
        
        else:
            return ERROR400
        
    else:
        serializer = PaginatorBusinessSerializer(data = request.GET)
        if not serializer.is_valid() or not check_request(request, serializer):
            return ERROR400
        
        promos = Promo.objects.none()

        countries = dict(request.GET).get("country")
        if countries:
            countries = [i for j in countries for i in j.split(",") ]
            countries.append(None)
            # https://stackoverflow.com/questions/14907525/how-can-i-chain-djangos-in-and-iexact-queryset-field-lookups
            q_list = map(lambda n: Q(target__country__iexact=n), countries)
            q_list = reduce(lambda a, b: a | b, q_list)
            promos = Promo.objects.filter(q_list).filter(user = request.user)
            # promos = promos | Promo.objects.filter(user = request.user).filter(target__country__isnull = True) 
            # promos = promos | Promo.objects.filter(user = request.user).filter(target__country__iexact__in = countries)
        else:
            promos = Promo.objects.filter(user = request.user)

        limit = serializer.validated_data["limit"]
        offset = serializer.validated_data["offset"]

        # https://stackoverflow.com/questions/7749216/django-order-by-date-but-have-none-at-end
        if serializer.validated_data["sort_by"] == "active_from":
            promos = promos.order_by(F(f"active_from").desc(nulls_last=True))
        elif serializer.validated_data["sort_by"] == "active_until":
            promos = promos.order_by(F(f"active_until").desc(nulls_first=True))
        else:
            promos = promos.order_by(f"-created_at")

        X_Total_Count = promos.count()
        promos = promos[offset:offset+limit]
        
        output = PromoListSerializer(promos, many=True).data
        output = edit_promo_output(output)
        return Response(output, headers={"X-Total-Count": X_Total_Count}, status=200)
        

@api_view(["PATCH", "GET"])
@permission_classes([IsAuthenticated])
@is_business
def get_and_edit_promo(request, id):
    try: promo = Promo.objects.filter(promo_id = id)
    except: return ERROR400
    if not promo.exists(): return Response({"status": "error", "message": "Промокод не найден."}, status=404)
    promo = promo.first()
    if promo.user != request.user: return Response({"status": "error", "message": "Промокод не принадлежит этой компании."}, status=403)
    
    if request.method == "PATCH":
        if "active_from" in request.data and "active_until" in request.data:
            if request.data["active_from"] > request.data["active_until"]: return ERROR400

        if "description" in request.data and request.data["description"] == None: request.data.pop("description")
        if "max_count" in request.data and request.data["max_count"] == None: request.data.pop("max_count")
        if "target" in request.data: target = request.data.pop("target")
        else: target = None

        serializer = UpdatePromoSerializer(promo, data = request.data)
        if not serializer.is_valid() or (promo.mode == "UNIQUE" and ("max_count" in serializer.validated_data and serializer.validated_data["max_count"] != 1)): return ERROR400
        
        if target != None:
            serializer2 = TargetSerializer(data = target)
            if not serializer2.is_valid(): return ERROR400

            if "age_from" in serializer2.validated_data and "age_until" in serializer2.validated_data:
                if serializer2.validated_data["age_from"] > serializer2.validated_data["age_until"]:
                    return ERROR400
                
            try: Target.objects.get(promo = promo).delete()
            except: return ERROR400

            target = Target(promo = promo, **serializer2.validated_data)
            target.save()

        serializer.save()

    promo = Promo.objects.filter(promo_id = id)
    output = PromoListSerializer(promo, many=True).data
    output = edit_promo_output(output)[0]
    return Response(output, status=200)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
@is_customer
def customer_feed(request):
    serializer = PaginatorCustomerSerializer(data = request.GET)
    if not serializer.is_valid():
        return ERROR400

    promos = Promo.objects.all()

    if dict(request.GET).get("active") != None:
        if bool(serializer.validated_data["active"]) == True:
            newpromo = Promo.objects.none()
            newpromo = newpromo | promos.filter(mode = "COMMON").annotate(promo = Func("used_count", function='jsonb_array_length', output_field=IntegerField())).filter(promo__lt = F("max_count"))
            newpromo = newpromo | promos.filter(mode = "UNIQUE").annotate(promo = Func("available_promo_unique", function='jsonb_array_length', output_field=IntegerField())).filter(promo__gt = 0)
            promos = newpromo.exclude(active_from__gt = datetime.date.today()).exclude(active_until__lt = datetime.date.today())
        else:
            newpromo = Promo.objects.none()
            newpromo = newpromo | promos.filter(mode = "COMMON").annotate(promo = Func("used_count", function='jsonb_array_length', output_field=IntegerField())).filter(promo__gte = F("max_count"))
            newpromo = newpromo | promos.filter(mode = "UNIQUE").annotate(promo = Func("available_promo_unique", function='jsonb_array_length', output_field=IntegerField())).filter(promo__lte = 0)
            newpromo = newpromo | promos.filter(active_from__gt = datetime.date.today())
            promos = newpromo | promos.filter(active_until__lt = datetime.date.today())

    if serializer.validated_data.get("category"):
        promos = promos.filter(target__categories__icontains = serializer.validated_data["category"])

    countries = [request.user.customer.customertarget.country, None]
    q_list = map(lambda n: Q(target__country__iexact=n), countries)
    q_list = reduce(lambda a, b: a | b, q_list)
    promos = promos.filter(q_list)

    promos = promos.exclude(target__age_from__gt = request.user.customer.customertarget.age).exclude(target__age_until__lt = request.user.customer.customertarget.age)

    limit = serializer.validated_data["limit"]
    offset = serializer.validated_data["offset"]

    promos = promos.order_by(f"-created_at")

    X_Total_Count = promos.count()
    promos = promos[offset:offset+limit]
    
    output = PromoListForCustomerSerializer(promos, many=True).data
    output = format_customers_feed(output, request.user)
    return Response(output, headers={"X-Total-Count": X_Total_Count}, status=200)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
@is_customer
def customer_promoid(request, id):
    try: promo = Promo.objects.filter(promo_id = id)
    except: return ERROR400
    if not promo.exists(): return Response({"status": "error", "message": "Промокод не найден."}, status=404)
    output = PromoListForCustomerSerializer(promo, many=True).data
    output = format_customers_feed(output, request.user)
    return Response(output[0], status=200)

@api_view(["POST", "DELETE"])
@permission_classes([IsAuthenticated])
@is_customer
def customer_promoid_like(request, id):
    try: promo = Promo.objects.filter(promo_id = id)
    except: return ERROR400
    if not promo.exists(): return Response({"status": "error", "message": "Промокод не найден."}, status=404)
    promo = promo.first()
    if request.method == "POST":
        promo.like_count.add(request.user)
        promo.save()
    else:
        promo.like_count.remove(request.user)
        promo.save()
    return Response({"status": "ok"}, status=200)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
@is_customer
def activate_promo(request, id):
    try: promo = Promo.objects.filter(promo_id = id)
    except: return ERROR400
    if not promo.exists(): return Response({"status": "error", "message": "Промокод не найден."}, status=404)

    countries = [request.user.customer.customertarget.country, None]
    q_list = map(lambda n: Q(target__country__iexact=n), countries)
    q_list = reduce(lambda a, b: a | b, q_list)
    promo = promo.filter(q_list)

    promo = promo.exclude(target__age_from__gt = request.user.customer.customertarget.age).exclude(target__age_until__lt = request.user.customer.customertarget.age)

    if not promo.exists(): return ERROR403
    promo = promo.first()
    
    if promo.active_from != None and promo.active_from > datetime.date.today(): return ERROR403
    if promo.active_until != None and promo.active_until < datetime.date.today(): return ERROR403

    if promo.mode == "COMMON":
        if len(promo.used_count) >= promo.max_count or not antifraud_check(request, promo): return ERROR403
        else:
            promo.used_count.append(request.user.id)
            promo.statistic.append(request.user.customer.customertarget.country.lower())
            promo.save()
            request.user.customer.activated_promos.insert(0, str(promo.promo_id))
            request.user.customer.save()
            return Response({"promo": promo.promo_common}, status=200)
    else:
        if len(promo.available_promo_unique) <= 0 or not antifraud_check(request, promo): return ERROR403
        else:
            code = promo.available_promo_unique.pop()
            promo.used_count.append(request.user.id)
            promo.statistic.append(request.user.customer.customertarget.country.lower())
            promo.save()
            request.user.customer.activated_promos.insert(0, str(promo.promo_id))
            request.user.customer.save()
            return Response({"promo": code}, status=200)
        
@api_view(["GET"])
@permission_classes([IsAuthenticated])
@is_customer
def promo_history(request):
    serializer = PaginatorCustomerSerializer(data = request.GET)
    if not serializer.is_valid(): return ERROR400

    limit = serializer.validated_data["limit"]
    offset = serializer.validated_data["offset"]
    
    data = request.user.customer.activated_promos
    X_Total_Count = len(data)
    data = data[offset:offset+limit]

    for i in range(len(data)):
        promo = PromoListForCustomerSerializer(Promo.objects.get(promo_id = data[i]))
        data[i] = promo.data
    data = format_customers_feed(data, request.user)
    
    return Response(data, headers={"X-Total-Count": X_Total_Count}, status=200)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
@is_business
def promo_statistic(request, id):
    try: promo = Promo.objects.filter(promo_id = id)
    except: return ERROR400
    if not promo.exists(): return Response({"status": "error", "message": "Промокод не найден."}, status=404)
    promo = promo.first()
    if promo.user != request.user: return Response({"status": "error", "message": "Промокод не принадлежит этой компании."}, status=403)
    
    total = len(promo.statistic)
    countries = []
    if total:
        for i in sorted(list(set(promo.statistic))):
            countries.append({"country": i, "activations_count": promo.statistic.count(i)})
        data = {"activations_count": total, "countries": countries}
    else:
        data = {"activations_count": total}
    
    return Response(data, status=200)