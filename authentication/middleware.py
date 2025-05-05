from django.http import HttpResponse

class HeadRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'HEAD':
            response = self.get_response(request)
            response.content = b''
            return response
        return self.get_response(request)
