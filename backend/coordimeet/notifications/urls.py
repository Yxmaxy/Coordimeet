from django.urls import path

from coordimeet.notifications import views

app_name = "coordimeet_notifications"

urlpatterns = [
    path("subscription/", views.PushSubscriptionView.as_view(), name="push_subscription"),
    path("service-worker-push/", views.ServiceWorkerPushView.as_view(), name="service_worker_push"),
]
