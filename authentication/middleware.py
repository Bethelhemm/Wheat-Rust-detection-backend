from django.utils.deprecation import MiddlewareMixin
import os
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse


class HeadRequestMiddleware(MiddlewareMixin):
    """
    Middleware to handle HTTP HEAD requests properly.
    """

    def process_request(self, request):
        if request.method == 'HEAD':
            request.method = 'GET'
            request._head_request = True

    def process_response(self, request, response):
        if getattr(request, '_head_request', False):
            response.content = b''
        return response

class CertificateXFrameOptionsMiddleware(MiddlewareMixin):
    """
    Middleware to allow embedding of certificate files (pdf, png, jpeg, jpg) in iframes by
    modifying the X-Frame-Options header for /media/certificates/ URLs.
    """

    ALLOWED_EXTENSIONS = {'.pdf', '.png', '.jpeg', '.jpg'}

    def process_response(self, request, response):
        if request.path.startswith('/media/certificates/'):
            ext = os.path.splitext(request.path)[1].lower()
            if ext in self.ALLOWED_EXTENSIONS:
                # Remove X-Frame-Options header to allow embedding
                if 'X-Frame-Options' in response:
                    del response['X-Frame-Options']
        return response
