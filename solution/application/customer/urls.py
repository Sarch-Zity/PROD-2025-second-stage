from django.urls import path
from users import views as users_views
from promo import views as promo_views
from comments import views as comments_views

urlpatterns = [
    path('auth/sign-up', users_views.customer_sign_up, name="csignup"),
    path('auth/sign-in', users_views.customer_sign_in, name="csignin"),
    path('profile', users_views.customer_profile, name="cprofile"),
    path('feed', promo_views.customer_feed, name="cfeed"),
    path('promo/history', promo_views.promo_history, name="cpromohistory"),
    path('promo/<str:id>', promo_views.customer_promoid, name="cpromoid"),
    path('promo/<str:id>/like', promo_views.customer_promoid_like, name="clikepromo"),
    path('promo/<str:id>/comments', comments_views.comment_promo, name="ccommentpromo"),
    path('promo/<str:id>/comments/<str:commentid>', comments_views.comment_id_promo, name="ccommentidpromo"),
    path('promo/<str:id>/activate', promo_views.activate_promo, name="cpromoactivate"),
]