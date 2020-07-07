from modules.constant import WASHMIX_TEAM_ORDER_DROPOFF, WASHMIX_TEAM_ORDER_PICK


def order_pickup(**kwargs):
    order = kwargs.get("order")
    user = kwargs.get("user")

    def message_formatter():
        return WASHMIX_TEAM_ORDER_PICK.format(
            user.first_name,
            user.profile.phone,
            order.pickup_address.address_line_1,
            "%s @ %s"
            % (
                order.pick_up_from_datetime.strftime("%A %m/%d"),
                order.pick_up_from_datetime.strftime("%l:%M %p"),
            ),
        )

    return message_formatter


def order_dropoff(**kwargs):
    order = kwargs.get("order")
    user = kwargs.get("user")

    def message_formatter():
        return WASHMIX_TEAM_ORDER_DROPOFF.format(
            user.first_name,
            user.profile.phone,
            order.dropoff_address.address_line_1,
            "%s @ %s"
            % (
                order.drop_off_from_datetime.strftime("%A %m/%d"),
                order.drop_off_from_datetime.strftime("%l:%M %p"),
            ),
        )

    return message_formatter
