from django.http import JsonResponse
from django.views import View

class RootView(View):
    def get(self, request):
        return JsonResponse({"message": "Welcome to the Wheat Rust Detection API"})

    def head(self, request):
        response = self.get(request)
        response.content = b""
        return response

def health_check(request):
    return JsonResponse({"status": "ok"}, status=200)
