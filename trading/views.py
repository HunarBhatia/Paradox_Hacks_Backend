from decimal import Decimal
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import redis
from django.conf import settings as django_settings
from trading.models import PortfolioSnapshot

redis_client = redis.Redis.from_url(django_settings.CELERY_BROKER_URL, decode_responses=True)
LEADERBOARD_KEY = "leaderboard:returns"

from services.price_service import get_price
from services.trade_service import execute_buy, execute_sell
from trading.models import Transaction, Order, PortfolioPosition
from trading.serializers import (
    BuySerializer, SellSerializer, OrderSerializer,
    TransactionSerializer
)


class BuyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BuySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = execute_buy(
                user=request.user,
                ticker=serializer.validated_data['ticker'].upper(),
                quantity=serializer.validated_data['quantity'],
                order_type=serializer.validated_data.get('order_type', 'MARKET'),
            )
            return Response(result, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SellView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SellSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = execute_sell(
                user=request.user,
                ticker=serializer.validated_data['ticker'].upper(),
                quantity=serializer.validated_data['quantity'],
            )
            return Response(result, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PlaceOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(
            user=request.user,
            ticker=serializer.validated_data['ticker'].upper(),
            order_type=serializer.validated_data['order_type'],
            quantity=serializer.validated_data['quantity'],
            target_price=serializer.validated_data['target_price'],
        )
        return Response({
            'id': order.id,
            'ticker': order.ticker,
            'order_type': order.order_type,
            'quantity': order.quantity,
            'target_price': float(order.target_price),
            'status': order.status,
            'created_at': order.created_at,
        }, status=status.HTTP_201_CREATED)


class CancelOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

        if order.status != 'PENDING':
            return Response({'error': f'Cannot cancel an order with status {order.status}.'}, status=status.HTTP_400_BAD_REQUEST)

        order.status = 'CANCELLED'
        order.save()
        return Response({'message': f'Order {order_id} cancelled successfully.'})


class PortfolioView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        positions = PortfolioPosition.objects.filter(user=request.user)
        holdings = []
        total_invested = Decimal('0')
        total_current = Decimal('0')

        for pos in positions:
            current_price = get_price(pos.ticker)
            if not current_price:
                continue

            current_price = Decimal(str(current_price))
            invested = (pos.avg_buy_price * pos.quantity).quantize(Decimal('0.01'))
            current_value = (current_price * pos.quantity).quantize(Decimal('0.01'))
            pnl = (current_value - invested).quantize(Decimal('0.01'))
            pnl_pct = ((pnl / invested) * 100).quantize(Decimal('0.01')) if invested else Decimal('0')

            holdings.append({
                'ticker': pos.ticker,
                'quantity': pos.quantity,
                'avg_buy_price': float(pos.avg_buy_price),
                'current_price': float(current_price),
                'invested': float(invested),
                'current_value': float(current_value),
                'pnl': float(pnl),
                'pnl_pct': float(pnl_pct),
            })

            total_invested += invested
            total_current += current_value

        total_pnl = (total_current - total_invested).quantize(Decimal('0.01'))
        total_pnl_pct = ((total_pnl / total_invested) * 100).quantize(Decimal('0.01')) if total_invested else Decimal('0')
        cash_balance = request.user.wallet.balance

        return Response({
            'holdings': holdings,
            'summary': {
                'total_invested': float(total_invested),
                'total_current_value': float(total_current),
                'total_pnl': float(total_pnl),
                'total_pnl_pct': float(total_pnl_pct),
                'cash_balance': float(cash_balance),
                'portfolio_value': float(total_current + cash_balance),
            }
        })


class TransactionHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transactions = Transaction.objects.filter(user=request.user)
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)


class PendingOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user, status='PENDING')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    
class PnlHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        snapshots = PortfolioSnapshot.objects.filter(
            user=request.user
        ).order_by('date').values(
            'date', 'total_value', 'cash_balance', 'invested_value', 'daily_pnl'
        )
        return Response(list(snapshots))


class LeaderboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        results = redis_client.zrevrange(LEADERBOARD_KEY, 0, 19, withscores=True)

        leaderboard = [
            {
                "rank": idx + 1,
                "username": username,
                "return_pct": round(score, 2),
            }
            for idx, (username, score) in enumerate(results)
        ]

        return Response(leaderboard)