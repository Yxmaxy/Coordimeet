from simple_notifications import views as simple_notifications_views

from django.utils.decorators import method_decorator

from coordimeet.users.decorators import with_coordimeet_user


class PushSubscriptionView(simple_notifications_views.PushSubscriptionView):
    permission_classes = []

    @method_decorator(with_coordimeet_user, name="dispatch")
    def post(self, request):
        request.user = request.coordimeet_user
        return super().post(request)

    @method_decorator(with_coordimeet_user, name="dispatch")
    def delete(self, request):
        request.user = request.coordimeet_user
        return super().delete(request)


class ServiceWorkerPushView(simple_notifications_views.ServiceWorkerPushView): ...
