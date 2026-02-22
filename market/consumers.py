import asyncio
import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

from services.price_service import get_multiple_prices

logger = logging.getLogger(__name__)

DEFAULT_SYMBOLS = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK']


class PriceConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()
        self.symbols = DEFAULT_SYMBOLS
        self.running = True
        asyncio.create_task(self.price_loop())
        logger.info(f'WebSocket connected: {self.channel_name}')

    async def disconnect(self, close_code):
        self.running = False
        logger.info(f'WebSocket disconnected: {self.channel_name}')

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            if symbols := data.get('symbols'):
                self.symbols = [s.upper() for s in symbols[:20]]
                await self.send(json.dumps({
                    'type': 'subscribed',
                    'symbols': self.symbols,
                }))
        except json.JSONDecodeError:
            pass

    async def price_loop(self):
        while self.running:
            try:
                prices = await asyncio.get_event_loop().run_in_executor(
                    None, get_multiple_prices, self.symbols
                )
                await self.send(json.dumps({
                    'type': 'price_update',
                    'data': prices,
                }))
            except Exception as e:
                logger.error(f'Price loop error: {e}')

            await asyncio.sleep(15)