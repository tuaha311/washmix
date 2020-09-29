def logging_middleware(get_response):
    def middleware(request):
        print(request.META)

        response = get_response(request)

        return response

    return middleware
