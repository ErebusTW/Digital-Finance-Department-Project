#把這個檔案丟到C:\\veighna_studio\Lib\site-packages\vnpy_ctastrategy\strategies
from datetime import time
from datetime import timedelta
from importlib.metadata import entry_points
from re import S
from vnpy_ctastrategy import (
    CtaTemplate,
    StopOrder,
    TickData,
    BarData,
    TradeData,
    OrderData,
    BarGenerator,
    ArrayManager
)
from datetime import datetime

class SimpleShortStrategy(CtaTemplate):
    """"""
    author = "Erebus"


    fixed_size = 1
    shortdate = []
    stock_dict = {}
    symbol = 0

    day_high = 0
    day_open = 0
    day_close = 0
    day_low = 0

    exit_time = time(hour=13, minute=20)

    parameters = ["fixed_size","stock_dict","symbol"]
    variables = ["shortdate"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super(SimpleShortStrategy, self).__init__(
            cta_engine, strategy_name, vt_symbol, setting
        )

        self.bg = BarGenerator(self.on_bar)
        self.am = ArrayManager()
        self.bars = []

    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.write_log("策略初始化")
        self.load_bar(1)
        self.shortdate.clear()

    def on_start(self):
        """
        Callback when strategy is started.
        """
        self.write_log("策略启动")

    def on_stop(self):
        """
        Callback when strategy is stopped.
        """
        self.write_log("策略停止")

    def on_tick(self, tick: TickData):
        """
        Callback of new tick data update.
        """
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """
        self.cancel_all()

        am = self.am
        am.update_bar(bar)
        if not am.inited:
            return

        self.bars.append(bar)
        if len(self.bars) <= 2:
            return
        else:
            self.bars.pop(0)
        last_bar = self.bars[-2]

        # New Day
        if last_bar.datetime.date() != bar.datetime.date():
            self.day_open = bar.open_price
            self.day_high = bar.high_price
            self.day_close = bar.close_price
            self.day_low = bar.low_price
            self.shortdate.append(bar.datetime.date())
        # Today
        else:
            self.day_high = max(self.day_high, bar.high_price)
            self.day_low = min(self.day_low, bar.low_price)
            self.day_close = bar.close_price

        if bar.datetime.time() < self.exit_time:
            if  self.symbol in self.stock_dict[datetime.strftime(bar.datetime.date(), "%Y%m%d")]:
                if self.pos == 0:
                    self.short(bar.close_price, self.fixed_size)
                    self.shortdate.clear()
            if self.pos < 0:
                if len(self.shortdate) >= 5:
                    self.cover(bar.close_price, abs(self.pos))

        # Close existing position
        else:
            if self.pos < 0:
                if len(self.shortdate) >= 4:
                    self.cover(bar.close_price, abs(self.pos))
    
        self.put_event()

    def on_order(self, order: OrderData):
        """
        Callback of new order data update.
        """
        pass

    def on_trade(self, trade: TradeData):
        """
        Callback of new trade data update.
        """
        self.put_event()

    def on_stop_order(self, stop_order: StopOrder):
        """
        Callback of stop order update.
        """
        pass