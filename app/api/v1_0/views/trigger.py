from rest_framework.generics import GenericAPIView
from rest_framework.response import Response


class TriggerView(GenericAPIView):
    def post(self, request, *args, **kwargs):
        return Response()
