from django.conf import settings

from rest_framework import serializers

"""
Raw webhook data example:
{
    "context": {
        "contact": {
            "channel": {
                "address": "OmjsM1zEBZZRLmo2YMhTZNIUxLI14nLV"
            }
        },
        "trigger": {
            "message": {
                "EventType": "onMessageSent",
                "InstanceSid": "IS75654a125c224f66bc1a1d581d5927c8",
                "Attributes": "{}",
                "DateCreated": "2020-09-14T02:41:08.986Z",
                "Index": "0",
                "From": "OmjsM1zEBZZRLmo2YMhTZNIUxLI14nLV",
                "MessageSid": "IM6badf37d2c77457783808850ee66f706",
                "Source": "SDK",
                "AccountSid": "AC388be19d2dc904fb0bc7bd6e0b018cf7",
                "ChannelSid": "CHc18e7d30d5b2428a82c6849d70fca92d",
                "RetryCount": "0",
                "ClientIdentity": "OmjsM1zEBZZRLmo2YMhTZNIUxLI14nLV",
                "WebhookType": "studio",
                "To": "CHc18e7d30d5b2428a82c6849d70fca92d",
                "Body": "oo",
                "ChannelAttributes": {
                    "status": "ACTIVE",
                    "long_lived": false,
                    "pre_engagement_data": {
                        "friendlyName": "Customer",
                        "isWebchatDemo": true,
                        "location": "https://demo.flex.twilio.com/chat?accountSid=AC388be19d2dc904fb0bc7bd6e0b018cf7&amp;flexFlowSid=FO06532466a75ec2b9e42ec7cbed8a1176"
                    },
                    "from": "Customer",
                    "channel_type": "web"
                },
                "WebhookSid": "WHa8f1d9bb0e354aceaeec0fa299f8c0d9"
            }
        },
        "widgets": {
            "Message": {
                "outbound": {
                    "WasEdited": false,
                    "DateUpdated": {
                        "era": 1,
                        "dayOfYear": 258,
                        "dayOfWeek": 1,
                        "dayOfMonth": 14,
                        "year": 2020,
                        "weekOfWeekyear": 38,
                        "millisOfDay": 9669000,
                        "monthOfYear": 9,
                        "hourOfDay": 2,
                        "minuteOfHour": 41,
                        "secondOfMinute": 9,
                        "millisOfSecond": 0,
                        "weekyear": 2020,
                        "yearOfEra": 2020,
                        "yearOfCentury": 20,
                        "centuryOfEra": 20,
                        "secondOfDay": 9669,
                        "minuteOfDay": 161,
                        "zone": {
                            "fixed": true,
                            "id": "UTC"
                        },
                        "millis": 1600051269000,
                        "chronology": {
                            "zone": {
                                "fixed": true,
                                "id": "UTC"
                            }
                        },
                        "afterNow": false,
                        "beforeNow": true,
                        "equalNow": false
                    },
                    "Attributes": "{}",
                    "DateCreated": {
                        "era": 1,
                        "dayOfYear": 258,
                        "dayOfWeek": 1,
                        "dayOfMonth": 14,
                        "year": 2020,
                        "weekOfWeekyear": 38,
                        "millisOfDay": 9669000,
                        "monthOfYear": 9,
                        "hourOfDay": 2,
                        "minuteOfHour": 41,
                        "secondOfMinute": 9,
                        "millisOfSecond": 0,
                        "weekyear": 2020,
                        "yearOfEra": 2020,
                        "yearOfCentury": 20,
                        "centuryOfEra": 20,
                        "secondOfDay": 9669,
                        "minuteOfDay": 161,
                        "zone": {
                            "fixed": true,
                            "id": "UTC"
                        },
                        "millis": 1600051269000,
                        "chronology": {
                            "zone": {
                                "fixed": true,
                                "id": "UTC"
                            }
                        },
                        "afterNow": false,
                        "beforeNow": true,
                        "equalNow": false
                    },
                    "Index": 1,
                    "From": "CHc18e7d30d5b2428a82c6849d70fca92d",
                    "AccountSid": "AC388be19d2dc904fb0bc7bd6e0b018cf7",
                    "Url": "https://chat.twilio.com/v2/Services/IS75654a125c224f66bc1a1d581d5927c8/Channels/CHc18e7d30d5b2428a82c6849d70fca92d/Messages/IMe850c7c0ffbd4576a8d73cdd09205588",
                    "Sid": "IMe850c7c0ffbd4576a8d73cdd09205588",
                    "ChannelSid": "CHc18e7d30d5b2428a82c6849d70fca92d",
                    "Type": "text",
                    "ServiceSid": "IS75654a125c224f66bc1a1d581d5927c8",
                    "To": "CHc18e7d30d5b2428a82c6849d70fca92d",
                    "Body": "Proxying started ..."
                }
            },
            "twiml": {
                "inbound": {
                    "EventType": "onMessageSent",
                    "InstanceSid": "IS75654a125c224f66bc1a1d581d5927c8",
                    "Attributes": "{}",
                    "DateCreated": "2020-09-14T02:42:25.014Z",
                    "Index": "3",
                    "From": "OmjsM1zEBZZRLmo2YMhTZNIUxLI14nLV",
                    "MessageSid": "IM790f8e8467604ed685a18be9ea2117eb",
                    "Source": "SDK",
                    "AccountSid": "AC388be19d2dc904fb0bc7bd6e0b018cf7",
                    "ChannelSid": "CHc18e7d30d5b2428a82c6849d70fca92d",
                    "RetryCount": "0",
                    "ClientIdentity": "OmjsM1zEBZZRLmo2YMhTZNIUxLI14nLV",
                    "WebhookType": "studio",
                    "To": "CHc18e7d30d5b2428a82c6849d70fca92d",
                    "Body": "kkk",
                    "ChannelAttributes": "{\"status\":\"ACTIVE\",\"long_lived\":false,\"pre_engagement_data\":{\"friendlyName\":\"Customer\",\"isWebchatDemo\":true,\"location\":\"https://demo.flex.twilio.com/chat?accountSid=AC388be19d2dc904fb0bc7bd6e0b018cf7&amp;flexFlowSid=FO06532466a75ec2b9e42ec7cbed8a1176\"},\"from\":\"Customer\",\"channel_type\":\"web\"}",
                    "WebhookSid": "WHa8f1d9bb0e354aceaeec0fa299f8c0d9"
                }
            }
        },
        "flow": {
            "flow_sid": "FWab31deda0047265332af3df7ec4cd7b4",
            "channel": {
                "address": "CHc18e7d30d5b2428a82c6849d70fca92d"
            },
            "sid": "FNdca715acd8ab0d1f6adeefd1e0b8f915"
        }
    },
    "account_sid": "AC388be19d2dc904fb0bc7bd6e0b018cf7",
    "flow_sid": "FWab31deda0047265332af3df7ec4cd7b4",
    "execution_sid": "FNdca715acd8ab0d1f6adeefd1e0b8f915",
    "step_sid": "FT62b2db7694652dccb8837f578321ed28",
    "encrypted": true
}
"""


class TwilioFlexWebhookSerializer(serializers.Serializer):
    """
    Request data from Twilio Flex Widget.
    Pretty form:
    {
        "message": "{{trigger.message.Body}}",
        "contact": "{{trigger.message.From}}"
    }

    Short form:
    {"message": "{{trigger.message.Body}}", "contact": "{{trigger.message.From}}"}
    """

    message = serializers.CharField()
    contact = serializers.CharField()

    def validate(self, attrs):
        client = self.context["request"].user.client

        # if client doesn't have an address
        # we can't handle pickup request
        if not client.main_address:
            raise serializers.ValidationError(
                detail="Client doesn't have an address.", code="no_pickup_address",
            )

        return attrs
