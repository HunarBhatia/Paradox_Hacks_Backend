from rest_framework import serializers
from trading.models import Transaction, Order


class BuySerializer(serializers.Serializer):
    ticker = serializers.CharField(max_length=20)
    quantity = serializers.IntegerField(min_value=1)
    order_type = serializers.ChoiceField(choices=['MARKET', 'LIMIT', 'STOP_LOSS'], default='MARKET')


class SellSerializer(serializers.Serializer):
    ticker = serializers.CharField(max_length=20)
    quantity = serializers.IntegerField(min_value=1)


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'ticker', 'order_type', 'quantity', 'target_price', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'ticker', 'action', 'quantity', 'price_at_execution',
                  'brokerage', 'total_value', 'order_type', 'pnl', 'timestamp']