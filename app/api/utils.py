import json


def transform_twilio_to_json(raw_string: str) -> dict:
    # we are replacing ' -> "
    # because Twilio send in Webhook very strangely formed data
    # enclosed in one quote '
    double_quoted_string = raw_string.replace("'", '"')

    return json.loads(double_quoted_string)
