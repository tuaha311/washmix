from unittest.mock import patch
from uuid import uuid4

from django.contrib.auth.models import User

from modules.helpers import (
    mock_add_customer,
    mock_get_card,
    mock_get_customer,
    mock_get_token,
    mocked_twilio_create,
)
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from billing.models import Card
from locations.models import Address
from orders.models import Order
from tests.conftest import fake
from users.models import Profile


class UsersTest(APITestCase):
    def test_add_user(self):
        """Test: Creating single user.

        Expected response: HTTP 201
        """
        client = APIClient()
        response = client.post(
            path="/users/",
            data={
                "users": [
                    {
                        "first_name": fake.first_name(),
                        "last_name": fake.last_name(),
                        "email": fake.safe_email(),
                        "password": "test{}".format(str(uuid4())[:5]),
                        "phone": "00000000",
                    }
                ]
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)

    def test_add_users(self):
        """Test: Creating multiple user.

        Expected response: HTTP 201
        """
        client = APIClient()
        response = client.post(
            "/users/",
            {
                "users": [
                    {
                        "first_name": "test_first",
                        "last_name": "test_last",
                        "password": "test321",
                        "email": "test@test.com",
                        "phone": "00000000",
                    },
                    {
                        "first_name": "test2_first",
                        "last_name": "test2_last",
                        "email": "test2@test2.com",
                        "password": "test2321",
                        "phone": "00000000",
                    },
                ]
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

    def test_users_params(self):
        """Test: Register user API, not provided with proper parameters.

        Expected Response: HTTP 400
        """
        client = APIClient()
        response = client.post(
            "/users/",
            {"users": [{"last_name": "test_last", "email": "321@test.com", "phone": "00000000",}]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_info_update(self):
        """Test: This test holds following cases.
        1- Creates user, followed by adding address against user.
        2- Edits email, address_line_1, last_name, first_name, city
        and than compares edited value at model level.
        3- Deletes user.
        4- And checks user should'nt exist.
        """
        client = APIClient()

        user_data = {
            "first_name": "sample_name",
            "last_name": "sample_last",
            "email": "sample@sample.com",
            "password": "sample321",
            "username": "sample@sample.com",
        }

        user = User(**user_data)
        user.save()

        user = User.objects.get(email="sample@sample.com")
        client.force_authenticate(user=user)

        response = client.patch(
            "/users/",
            data={
                "users": [
                    {
                        "addresses": [
                            {
                                "address_line_1": "sample address",
                                "city": "LA",
                                "state": "california",
                                "zip_code": "24AFV",
                            },
                            {
                                "address_line_1": "sample address",
                                "city": "LA",
                                "state": "california",
                                "zip_code": "43fsd",
                            },
                        ]
                    }
                ]
            },
            format="json",
        )

        self.assertEqual(Address.objects.count(), 2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        #  Updating user info
        response = client.patch(
            "/users/",
            data={
                "users": [
                    {
                        "email": "sample321@sample.com",
                        "password": "sample321",
                        "first_name": "",
                        "last_name": "",
                        "addresses": [
                            {
                                "id": response.data["user"][0]["address_ids"][0],
                                "address_line_1": "",
                                "city": "NYC",
                            }
                        ],
                    }
                ]
            },
            format="json",
        )

        user = User.objects.get(email="sample321@sample.com")

        self.assertEqual(user.email, user.username)
        self.assertEqual(user.first_name, "")
        self.assertEqual(user.last_name, "")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        address = Address.objects.get(user=user, id=response.data["user"][0]["address_ids"][0])
        self.assertEqual(address.city, "NYC")
        self.assertEqual(address.address_line_1, "")

        # Deleting user
        user_id = user.id
        response = client.delete("/users/{0}".format(user_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Getting same user, expected behavior is it must not exist
        response = client.get("/users/{0}".format(user_id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch("middleware.MessageClient.send_message", side_effect=mocked_twilio_create)
    def test_user_orders(self, _):
        """Test: Creates user, tries to add Order against user.
        but due to absence of address against user it throws 404.
        Adds address against user.
        Adds Order.
        Edits order.
        Edits order with missing params.
        """
        client = APIClient()
        user_data = {
            "first_name": "sample_name",
            "last_name": "sample_last",
            "email": "sample@sample.com",
            "password": "sample321",
            "username": "sample@sample.com",
        }

        user = User(**user_data)
        user.save()
        Profile.objects.create(user=user, phone="000000000000")

        user = User.objects.get(email="sample@sample.com")
        client.force_authenticate(user=user)

        response = client.post(
            "/orders/",
            data={
                "order": {
                    "pick_up_from_datetime": "2017-07-01T01:00:00",
                    "pick_up_to_datetime": "2017-07-01T02:00:00",
                    "drop_off_from_datetime": "2017-07-05T01:00:00",
                    "drop_off_to_datetime": "2017-07-05T02:00:00",
                    "instructions": "sample instructions for testing purpose",
                    "additional_notes": "sample notes",
                }
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Creation of order when user address exist.
        address_data = {
            "address_line_1": "sample address",
            "state": "California",
            "city": "LA",
            "zip_code": "54782A",
        }
        address = Address.objects.create(user=user, **address_data)
        address.save()

        # At this stage we don't have order against user so it should be
        # 404 not found.
        response = client.get("/orders/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = client.post(
            "/orders/",
            data={
                "order": {
                    "pick_up_from_datetime": "2017-07-01T01:00:00",
                    "pick_up_to_datetime": "2017-07-01T02:00:00",
                    "drop_off_from_datetime": "2017-07-05T01:00:00",
                    "drop_off_to_datetime": "2017-07-05T02:00:00",
                    "instructions": "sample instructions for testing purpose",
                    "additional_notes": "sample notes",
                }
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = client.get("/orders/")
        self.assertEqual(response.data["Orders"]["count"], 1)

        # Editing order
        response = client.patch(
            "/orders/",
            data={
                "order": {
                    "id": str(Order.objects.get(user=user).id),
                    "instructions": "updated instructions",
                }
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Editing order but missing required field, must end with 400 bad request
        response = client.put(
            "/orders/",
            data={
                "order": {
                    "id": str(Order.objects.get(user=user).id),
                    "instructions": "updated instructions",
                }
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("modules.helpers.StripeHelper.add_customer", side_effect=mock_add_customer)
    @patch("modules.helpers.StripeHelper.get_customer", side_effect=mock_get_customer)
    @patch("modules.helpers.StripeHelper.get_token", side_effect=mock_get_token)
    @patch("modules.helpers.StripeHelper.get_card", side_effect=mock_get_card)
    @patch("middleware.MessageClient.send_message", side_effect=mocked_twilio_create)
    def test_user_purchase(self, *args):
        """
        Test stripe api with incomplete params, then checks if DB is properly tracking
        string_user_id and stripe_card_id.
        :param args:
        :return:
        """
        client = APIClient()
        user_data = {
            "first_name": "sample_name",
            "last_name": "sample_last",
            "email": "sample@sample.com",
            "password": "sample321",
            "username": "sample@sample.com",
        }

        user = User(**user_data)
        user.save()
        Profile.objects.create(user=user, phone="000000000000")
        client.force_authenticate(user=user)

        response = client.post(
            "/user_purchase/add_card/",
            data={"card": {"expiry_year": 2022, "expiry_month": 10}},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = client.post(
            "/user_purchase/add_card/",
            data={"card": {"card_number": "xxxxxxxxxx", "expiry_year": 2022, "expiry_month": 10,}},
            format="json",
        )

        self.assertEqual(user.profile.stripe_customer_id, "sample_id")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        card_list = Card.objects.get(user=user)
        self.assertEqual(card_list.stripe_card_id, "sample_card_id")
