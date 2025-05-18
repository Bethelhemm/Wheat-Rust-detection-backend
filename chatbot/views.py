from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .gemini_client import get_gemini_response

class ChatbotAPIView(APIView):
    def post(self, request):
        user_message = request.data.get('message', '')
        if not user_message:
            return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)

        prompt = f"You are a helpful agricultural assistant specialized in wheat rust detection. Answer the user's query accordingly: {user_message}"
        reply = get_gemini_response(prompt)

        return Response({'reply': reply})
