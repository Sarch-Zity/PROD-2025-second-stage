from django.urls import path
from users import views as users_views
from promo import views as promo_views

urlpatterns = [
    path('auth/sign-up', users_views.business_sign_up, name="bsignup"),
    path('auth/sign-in', users_views.business_sign_in, name="bsignin"),
    path('promo', promo_views.get_and_create_promo, name="createpromo"),
    path('promo/<str:id>', promo_views.get_and_edit_promo, name="createpromo"),
    path('promo/<str:id>/stat', promo_views.promo_statistic, name="promostatistic"),
]