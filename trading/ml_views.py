from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from services.csv_export_service import build_trade_dataframe
from services.ml_service import get_ml_insights


class TradeInsightsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        df = build_trade_dataframe(request.user)

        if df.empty:
            return Response({
                'status': 'insufficient_data',
                'message': 'You need at least one completed trade (a buy followed by a sell) before we can analyze your trading patterns.',
                'insights': []
            })

        # Market state columns only populate during weekday market hours
        # market_cols = ['trend', 'volatility', 'rsi_value']
        # missing = [c for c in market_cols if c not in df.columns or df[c].isnull().all()]

        # if missing:
        #     return Response({
        #         'status': 'insufficient_market_data',
        #         'message': 'Market state data is only available for trades made during NSE market hours on weekdays. Please make trades during 9:15 AM - 3:30 PM IST for full analysis.',
        #         'trades_found': len(df)
        #     })

        try:
            report, analytics = get_ml_insights(df)
            return Response({
                'status': 'ok',
                'total_completed_trades': len(df),
                'analytics': analytics,
                'report': report,
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=500)