from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from chatbot.models import ChatMessage
from services.chatbot_services import get_chatbot_response


class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_message = request.data.get('message', '').strip()

        if not user_message:
            return Response(
                {'error': 'Message cannot be empty'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Load last 20 messages from DB and convert to history format
        recent_messages = ChatMessage.objects.filter(
            user=request.user
        ).order_by('-timestamp')[:20]

        history = [
            {'role': msg.role, 'content': msg.content}
            for msg in reversed(list(recent_messages))
        ]

        # Call the chatbot function
        result = get_chatbot_response(
            user_message=user_message,
            history=history
        )

        # Save both messages to DB
        ChatMessage.objects.create(
            user=request.user,
            role='user',
            content=user_message
        )
        ChatMessage.objects.create(
            user=request.user,
            role='assistant',
            content=result['response']
        )

        return Response({'response': result['response']})