from simple_notifications import views as simple_notifications_views

from django.utils.decorators import method_decorator

from coordimeet.users.decorators import with_coordimeet_user


class PushSubscriptionView(simple_notifications_views.PushSubscriptionView):
    permission_classes = []

    @method_decorator(with_coordimeet_user, name="dispatch")
    def post(self, request, app_name: str):
        request.user = request.coordimeet_user
        return super().post(request, app_name)

    @method_decorator(with_coordimeet_user, name="dispatch")
    def delete(self, request, app_name: str):
        request.user = request.coordimeet_user
        return super().delete(request, app_name)


class SubscriptionStatusView(simple_notifications_views.SubscriptionStatusView):
    permission_classes = []

    @method_decorator(with_coordimeet_user, name="dispatch")
    def get(self, request, app_name: str):
        request.user = request.coordimeet_user
        return super().get(request, app_name)


class ServiceWorkerPushView(simple_notifications_views.ServiceWorkerPushView): ...
