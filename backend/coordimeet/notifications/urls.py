from django.urls import path

from coordimeet.notifications import views

app_name = "coordimeet_notifications"

urlpatterns = [
    path("subscribe/<str:app_name>/", views.PushSubscriptionView.as_view(), name="subscribe_push"),
    path("unsubscribe/<str:app_name>/", views.PushSubscriptionView.as_view(), name="unsubscribe_push"),
    path("status/<str:app_name>/", views.SubscriptionStatusView.as_view(), name="subscription_status"),
    path("service-worker-push/", views.ServiceWorkerPushView.as_view(), name="service_worker_push"),
]
