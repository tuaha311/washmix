import logging

logger = logging.getLogger(__name__)


def logging_middleware(get_response):
    def middleware(request):
        logger.info(request.META)

        response = get_response(request)

        return response

    return middleware
