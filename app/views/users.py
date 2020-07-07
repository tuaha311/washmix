import logging

from django.contrib.auth.models import User
from djoser.views import ActivationView
from rest_framework import status
from rest_framework.response import Response
from rest_framework_social_oauth2.authentication import SocialAuthentication

from custom_permission.custom_token_authentication import (
    CustomIsAdminUser,
    CustomSocialAuthentication,
    IsAuthenticatedOrPost,
    RefreshTokenAuthentication,
    account_activation_token,
)
from modules.constant import AppUsers
from modules.helpers import StripeHelper, wm_exception
from serializers.user_serializer import UserDataSerializer, UserSerializer
from views.stripe import Cards

logging.basicConfig(level=logging.ERROR, format="%(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# from rest_framework.authentication import TokenAuthentication
# from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication


class Users(Cards):
    authentication_classes = (
        RefreshTokenAuthentication,
        CustomSocialAuthentication,
        SocialAuthentication,
    )
    permission_classes = (IsAuthenticatedOrPost, CustomIsAdminUser)

    def patch(self, request, *args, **kwargs):
        """
        Currently this api lets you edit User information, following is the json format for it
        {
            "users": {
                    "first_name": "sample",
                    "last_name": "sample_last",
                    "password": "sample321"
            }
        }
        If you want to add/edit address at the same time while editing user following 
        is the format for json
        {
            "users": {
                    "first_name": "sample",
                    "last_name": "sample_last",
                    "password": "sample321",
                    "addresses": [
                                {
                                "id": 12,
                                "address_line_1": "sample address",
                                "state": "California",
                                "city": "LA",
                                "zip_code": "32532"
                                },
                                {
                                 "address_line_1": "sample address"
                                }
                    ]
            }
        }
       
       if id is provided while editing address it will update desired attribute if not
       it will add new address against the user
       
        For Adding address following fields are must:
        address_line_1
        city
        state
        zip code
     
        "address_line_2": any address which required second line must come under this field.e.g
            "address_line_1": 225 Eastridge Drive
            "address_line_2": Apt #34
        :param request: 
        :param format: 
        :return: User id for which user_info or address has been updated.
        """
        if request.user:
            return self.process_update(request, is_partial=True, user_id=kwargs.get("id"))

    def put(self, request, *args, **kwargs):
        if request.user:
            return self.process_update(request)

    def post(self, request, *args, **kwargs):
        """
        This api provide an option for adding Multiple user following is the format for json
        {
        
        "users": [
                {
                    "first_name": "sample name",
                    "last_name": "sample_last",
                    "email": "sample@sample.com",
                    "password": "sample321",
                    "phone": "00000000"
                }
            ]
        }
        All the fields mentioned in json are a must.
        :param request: 
        :param format: 
        :return: List of user ids successfully created.
        """
        request_body = request.data.get("users")
        # Data must be provided and validated
        validation = UserSerializer(data=request_body, many=True)
        validation.is_valid(raise_exception=True)
        created_user_ids = validation.save()

        response_dict = {"users": created_user_ids}
        user = User.objects.get(id=created_user_ids[-1]["user"])
        if request.data.get("users", [{}])[-1].get(
            "app_users"
        ) == AppUsers.REGULAR_USERS.value and (request.user.is_staff or request.user.is_superuser):
            kwargs = dict()
            kwargs["type"] = "add_card"
            response = super(Users, self).post(request_body[-1], user=user, **kwargs)
            response_dict.update({"add_card": response.data.get("message")})

            kwargs["type"] = "buy_package"
            kwargs["id"] = response.data.get("card_id") or -1
            response = super(Users, self).post(request_body[-1], user=user, **kwargs)
            response_dict.update({"buy_package": response.data.get("message")})

        return Response(data=response_dict, status=status.HTTP_201_CREATED, content_type="json")

    def get(self, request, *args, **kwargs):
        """
        This api gets any user, using user id.
        :param request: 
        :param args: 
        :param kwargs: holds query param mapping.
        :return: Json response, containing data for users.
        """
        user = None
        kwargs = dict(filter(lambda val: val[1], self.kwargs.items()))
        try:

            if kwargs.get("id") and kwargs.get("app_users"):
                user = User.objects.filter(
                    id=kwargs.get("id"), profile__app_users=kwargs.get("app_users")
                )
                user = UserDataSerializer(user, many=True)
            if kwargs.get("id"):
                user = User.objects.get(id=kwargs.get("id"))
                user = UserDataSerializer(instance=user, stripes_helper=StripeHelper())
            elif kwargs.get("app_users"):
                user = User.objects.filter(profile__app_users=kwargs.get("app_users"))
                user = UserDataSerializer(user, many=True)
            else:
                user = User.objects.all()
                user = UserDataSerializer(user, many=True)

            if user:
                return Response(
                    data={"users": user.data}, status=status.HTTP_200_OK, content_type="json",
                )
        except User.DoesNotExist:
            return Response(
                data={"users": "User Doesn't exist"},
                status=status.HTTP_404_NOT_FOUND,
                content_type="json",
            )

    def delete(self, request, *args, **kwargs):
        """
        Api deletes any user using user id.
        :param request: 
        :param args: 
        :param kwargs: holds query param mapping
        :return: response json
        """
        if kwargs.get("id"):
            try:
                user = User.objects.get(**kwargs)
            except User.DoesNotExist:
                return Response(
                    data={"users": "User Doesn't exist"},
                    status=status.HTTP_404_NOT_FOUND,
                    content_type="json",
                )
            user.delete()
            return Response(
                data={"users": "User Deleted"}, status=status.HTTP_200_OK, content_type="json",
            )

        return Response(
            data={"users": "User ID is must"},
            status=status.HTTP_404_NOT_FOUND,
            content_type="json",
        )

    @wm_exception
    def process_update(self, request, is_partial=False, user_id=None):
        """
        This method handles and update request.
        :param request: 
        :param is_partial: is partial helps identify type of request whether its a put or partial
        update.
        :return: returns list containing user id and list of ids for addresses which has been
        updated
        """
        try:
            user_info = request.data["users"]
            if user_id:
                user_info[0].update({"user_id": user_id})
        except Exception as error:
            return "", status.HTTP_400_BAD_REQUEST, {"detail": 'Must be a "users" key'}
            # return Response(
            #     data={'detail': 'Must be a "users" key'},
            #     status=status.HTTP_400_BAD_REQUEST,
            #     content_type='json'
            # )

        user_id = []
        # try:
        if user_info:
            user = UserSerializer(
                instance=request.user,
                data=user_info,
                partial=is_partial,
                many=True,
                context={"request": self.request},
            )
            user.is_valid(raise_exception=True)
            user_id.append(user.save())

        # except APIException as error:
        #     return Response(
        #         data={'detail': error.detail[0]},
        #         status=error.status_code,
        #         content_type='json'
        #     )
        # except Exception as error:
        #     return Response(
        #         data={'detail': error.detail[0]},
        #         status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        #         content_type='json'
        #     )

        # return Response(
        #     data={'user': user_id},
        #     status=status.HTTP_200_OK,
        #     content_type='json'
        # )
        return "", status.HTTP_200_OK, {"user": user_id}


class UserActivationView(ActivationView):
    token_generator = account_activation_token
