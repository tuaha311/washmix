from custom_permission.custom_token_authentication import (
    CustomIsAdminUser,
    CustomSocialAuthentication,
    IsAuthenticatedOrPost,
    RefreshTokenAuthentication,
)
from core.models import Product
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_social_oauth2.authentication import SocialAuthentication
from serializer.products_serializer import ProductSerializer


class ProductView(APIView):
    authentication_classes = (
        RefreshTokenAuthentication,
        CustomSocialAuthentication,
        SocialAuthentication,
    )
    permission_classes = (IsAuthenticatedOrPost, CustomIsAdminUser)

    def post(self, request, **kwargs):

        product = None
        product_ser = None
        try:
            product_ser = ProductSerializer(data=request.data)
            product_ser.is_valid(raise_exception=True)
            product = product_ser.save()
        except APIException as error:
            raise error
        except Exception:
            pass

        return Response(
            data=(product and ProductSerializer(product).data)
            or {"message": "Unexpected error occurred"},
            status=(product_ser and status.HTTP_201_CREATED)
            or status.HTTP_500_INTERNAL_SERVER_ERROR,
            content_type="json",
        )

    def patch(self, request, **kwargs):

        product = None
        message = None
        try:
            _instance = Product.objects.get(id=request.data.get("id"))
            product_ser = ProductSerializer(data=request.data, instance=_instance, partial=True)
            product_ser.is_valid(raise_exception=True)
            product = product_ser.save()
        except Product.DoesNotExist:
            message = 'Product doesn"t exist'
        except APIException as error:
            raise error
        except Exception:
            pass

        return Response(
            data=(product and ProductSerializer(product).data)
            or {"message": message or "Unexpected error occurred"},
            status=status.HTTP_201_CREATED,
            content_type="json",
        )

    def get(self, request, **kwargs):
        products = None
        try:
            products = ProductSerializer(Product.objects.get(**kwargs)).data
        except Product.DoesNotExist as error:
            pass

        return Response(
            data=products or {"message": "No product found"},
            status=(products and status.HTTP_200_OK) or status.HTTP_404_NOT_FOUND,
            content_type="json",
        )
