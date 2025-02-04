from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from users.authentication import is_customer
from rest_framework.permissions import IsAuthenticated
from .serializers import CommentSerializer, CommentListSerializer, PaginatorSerializer
from promo.models import Promo
from .models import Comment
ERROR400 = Response({"status": "error", "message": "Ошибка в данных запроса."}, status=400)

@api_view(["POST", "GET"])
@permission_classes([IsAuthenticated])
@is_customer
def comment_promo(request, id):
    try: promo = Promo.objects.filter(promo_id = id)
    except: return ERROR400
    if not promo.exists(): return Response({"status": "error", "message": "Промокод не найден."}, status=404)
    promo = promo.first()

    if request.method == "POST":
        serializer = CommentSerializer(data = request.data)
        if not serializer.is_valid():
            return ERROR400
        comment = Comment(user = request.user, promo = promo, **serializer.validated_data)
        comment.save()
        serializer = CommentListSerializer(comment)
        return Response(serializer.data, status=201)
    else:
        serializer = PaginatorSerializer(data = request.GET)
        if not serializer.is_valid(): return ERROR400
        offset = serializer.validated_data["offset"]
        limit = serializer.validated_data["limit"]
        
        promos = promo.comments.all().order_by("-created_at")
        X_Total_Count = promos.count()

        serializer = CommentListSerializer(promos[offset:offset + limit], many=True)
        return Response(serializer.data, headers={"X-Total-Count": X_Total_Count}, status=200)

@api_view(["PUT", "GET", "DELETE"])
@permission_classes([IsAuthenticated])
@is_customer
def comment_id_promo(request, id, commentid):
    try: promo = Promo.objects.filter(promo_id = id)
    except: return ERROR400
    if not promo.exists(): return Response({"status": "error", "message": "Такого промокода или комментария не существует."}, status=404)
    promo = promo.first()
    try: comment = promo.comments.filter(uuid = commentid)
    except: return ERROR400
    if not comment.exists(): return Response({"status": "error", "message": "Такого промокода или комментария не существует."}, status=404)
    comment = comment.first()

    if request.method == "PUT":
        if comment.user != request.user: return Response({"status": "error", "message": "Комментарий не принадлежит пользователю."}, status=403)
        serializer = CommentSerializer(comment, data = request.data)
        if serializer.is_valid(): serializer.save()
        else: return ERROR400
    elif request.method == "DELETE":
        if comment.user != request.user: return Response({"status": "error", "message": "Комментарий не принадлежит пользователю."}, status=403)
        comment.delete()
        return Response({"status": "ok"}, status=200)

    serializer = CommentListSerializer(comment)
    return Response(serializer.data, status=200)