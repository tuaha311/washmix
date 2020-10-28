from rest_framework.generics import GenericAPIView
from rest_framework.request import Request


class WelcomePrepareView(GenericAPIView):
    def post(self, request: Request, *args, **kwargs):
        pass
