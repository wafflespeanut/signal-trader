import unittest

from .errors import CloseTradeException, MoveStopLossException, ModifyTargetsException
from .signal import (AS, BAW, BFP, BFP2, BK, BPS, BVIP, BVIP2, C, CC, CCC, CCS, CEP, CY, E, EBS, FWP,
                     FXVIP, HBTCV, JMP, JPC, KBV, KCE, KK, KSP, KVIP, LVIP, MCVIP, MVIP, PBF, PHVIP, PVIP,
                     RM, RWS, SLVIP, SPP, SS, TCA, TVIPAW, VIPBB, VIPBS, VIPCC, VIPCS, W, WC, YCP, RESULTS, Signal)


class TestSignal(unittest.TestCase):
    def _assert_signal(self, cls, text, sig, risk_factor=None):
        s = cls.parse(Signal.sanitized(text))
        self.assertEqual(s.coin, sig.coin)
        self.assertEqual(s.entries, sig.entries)
        self.assertEqual(s.is_long, sig.is_long)
        self.assertEqual(s.sl, sig.sl)
        self.assertEqual(s.targets, sig.targets)
        self.assertEqual(s.leverage, sig.leverage)
        self.assertEqual(s.risk, sig.risk)
        self.assertEqual(s.tag, sig.tag if cls == RESULTS else cls.__name__)
        self.assertEqual(s.force_limit_order, sig.force_limit_order)


class TestRESULTS(TestSignal):
    def test_1(self):
        self._assert_signal(RESULTS, """
c ETH
e 1830 1740
t 1850 1870 1920 1980 2050
sl 1650
l 100
r 0.5""", Signal("ETH", [1830, 1740], [1850, 1870, 1920, 1980, 2050], 1650, 100, 0.5))

    def test_2(self):
        self._assert_signal(RESULTS, """
c etc
e 40.2 38
t 40.6 41.2 42 43.5 46
sl 37
l 75
force""", Signal("ETC", [40.2, 38], [40.6, 41.2, 42, 43.5, 46], 37, 75, force_limit=True))

    def test_3(self):
        self._assert_signal(RESULTS, """
c 1inch
e 2.5
t 5.3""", Signal("1INCH", [2.5], [5.3]))

    def test_4(self):
        tag = None
        try:
            self._assert_signal(RESULTS, """cancel my_tag""", None)
        except CloseTradeException as exp:
            tag = exp.tag
        self.assertEqual(tag, "my_tag")

    def test_5(self):
        self._assert_signal(RESULTS, "long akro sl 0.05", Signal("AKRO", is_long=True, sl=0.05))

    def test_6(self):
        tag, sl = None, None
        try:
            self._assert_signal(RESULTS, """change my_tag sl 25.45""", None)
        except MoveStopLossException as err:
            tag, sl = err.tag, err.price
        self.assertEqual(tag, "my_tag")
        self.assertEqual(sl, 25.45)

    def test_7(self):
        tag, tgts = None, None
        try:
            self._assert_signal(RESULTS, """change my_tag tp 25 30 34""", None)
        except ModifyTargetsException as err:
            tag, tgts = err.tag, err.targets
        self.assertEqual(tag, "my_tag")
        self.assertEqual(tgts, [25, 30, 34])

    def test_8(self):
        self._assert_signal(RESULTS, "long chr 0.25 sl 0.23 tp 0.27 0.29",
                            Signal("CHR", [0.25], [0.27, 0.29], 0.23, is_long=True))


class TestBFP(TestSignal):
    def test_1(self):
        self._assert_signal(
            BFP, """Binance Futures  Signal
Long/Buy #1INCH/USDT 3.2605
Targets 3.2735 - 3.2865 - 3.3061 - 3.3420 - 3.3909
Stoploss 3.1626
Leverage 5-10x
By (@BFP)
👆🏼👆🏼This is an Early signal. Buy #LINK when it comes around the entry price and maintain the stop loss """
            """- Just Trade with 3 to 5% of Total funds""",
            Signal("1INCH", [3.2605], [3.2735, 3.2865, 3.3061, 3.342, 3.3909], 3.1626))

    def test_2(self):
        s = Signal("BLZ", [28390], [28500, 28615, 28730, 28950, 29525], 26970)
        self._assert_signal(
            BFP, """Binance Future Signal
👇🏻👇🏻Early Signal - (IMPORTANT) This Trade should only be made, when the market price touches the  ENTRY POINT
Long/Buy #BLZ/USDT ️
Entry Point - 28390
Targets: 28500 - 28615 - 28730 - 28950 - 29525
Leverage - 10x
Stop Loss - 26970
By (@BFP)
✅✅Maintain the stop loss & Just Trade with 3 to 5% of Total funds""", s)
        s.correct(0.0283)
        self.assertAlmostEqual(s.entries[0], 0.02839)
        for e1, e2 in zip(s.targets, [0.028498899, 0.02861385, 0.02872885, 0.0289478, 0.02951925]):
            self.assertAlmostEqual(e1, e2)
        self.assertAlmostEqual(s.sl, 0.02697)
        self.assertAlmostEqual(s.fraction, 0.007597183)
        self.assertAlmostEqual(s.risk_reward, 0.795, places=3)

    def test_3(self):
        self._assert_signal(
            BFP, """Binance Future Signal
👇🏻Early Signal - (IMPORTANT) This Trade should only be made, when the market price touches the  ENTRY POINT

Short/Sell #ALICE/USDT ️

Entry Point - 5.930

Targets: 5.905 - 5.885 - 5.855 - 5.815 - 5.690
Leverage - 10x
Stop Loss - 6.290
By (@BFP)
✅✅Maintain the stop loss & Just Trade with 3 to 5% of Total funds""",
            Signal("ALICE", [5.93], [5.905, 5.885, 5.855, 5.815, 5.69], 6.29))

    def test_4(self):
        self._assert_signal(
            BFP, """Binance Future Signal
👇🏻👇🏻Early Signal - (IMPORTANT) This Trade should only be made, when the market price touches the  ENTRY POINT

Long/Buy #SAND/USDT ️

Entry Point - 35145

Targets: 35285 - 35425 - 35565 - 35845 - 36550
Leverage - 10x
Stop Loss - 33030
By (@BFP)
✅✅Maintain the stop loss & Just Trade with 3 to 5% of Total funds""",
            Signal("SAND", [35145], [35285, 35425, 35565, 35845, 36550], 33030))


class TestBPS(TestSignal):
    def test_1(self):
        self._assert_signal(
            BPS, """Binance Futures/Bitmex/Bybit/Bitseven Signal# 1325
Get into Long #1INCH/USDT @ 1.76
Leverage – 10x
Target - 1.77-1.78-1.81-1.86
Stop Loss - 1.68""", Signal("1INCH", [1.76], [1.77, 1.78, 1.81, 1.86], 1.68))

    def test_2(self):
        coin = None
        try:
            self._assert_signal(
                BPS, """(in reply to BPS)
> Binance Futures/Bitmex/Bybit/Bitseven Signal# 1327
> Get into Long #LTC/USDT @ 174…
Exit trade with minor loss""", None)
        except CloseTradeException as exp:
            coin = exp.coin
        self.assertEqual(coin, "LTC")


class TestCCS(TestSignal):
    def test_1(self):
        self._assert_signal(CCS, """📊 FUTURES (BINANCE)

#ALGOUSDT

LONG Below : 1.038

MAX 👉5x-7x LEVERAGE Hold

TAKE PROFIT:1.065+""", Signal("ALGO", [1.038], [1.065]))

    def test_2(self):
        self._assert_signal(
            CCS, """📊 FUTURES (BINANCE)

#FLMUSDT

LONG Below : 0.5820-0.5750

MAX 👉5x-7x LEVERAGE Hold

TAKE PROFIT: 0.6055|0.6330+""", Signal("FLM", [0.582, 0.575], [0.6055, 0.633]))

    def test_3(self):
        self._assert_signal(
            CCS, """📊 FUTURES (BINANCE)

#TRBUSDT

LONG Below : 62.00

MAX 👉5x-7x LEVERAGE Hold

TAKE PROFIT: 64.20|65.10|69.10+

SL: 58.85""", Signal("TRB", [62], [64.2, 65.1, 69.1], 58.85))


class TestFWP(TestSignal):
    def test_1(self):
        self._assert_signal(
            FWP, """#DOGEUSDT #LONG

BUY : 0.3400$- 0.3650$
TAKE PROFIT:
TARGET 1 : 0.3850$
TARGET 2 : 0.4000$
TARGET 3 : 0.4140$
TARGET 4 : 0.4300$
TARGET 5 : 0.4400$
TARGET 6 : 0.4500$
TARGET 7  : 0.4600$
TARGET 8  : 0.4700$

❗️STOL LOSS : 0.28$

Use 2% Fund Only

LEVERAGE:  10X-20X (CROSS)

BUY & HOLD ✅""", Signal("DOGE", [0.34, 0.365], [0.385, 0.4, 0.414, 0.43, 0.44, 0.45, 0.46, 0.47],
                        0.28))

    def test_2(self):
        self._assert_signal(
            FWP, """#ONT/USDT #LONG
(BINANCE FUTURES )
BUY : 2.25$- 2.38$
TAKE PROFIT:
TARGET 1 : 2.52$
TARGET 2 : 2.60$
TARGET 3 : 2.67$
TARGET 4 : 2.73$
TARGET 5 : 2.80$
TARGET 6 : 2.88$
TARGET 7 : 2.98$

❗️STOP LOSS :2.15$

Use 2% Fund Only ❗️

LEV :  10X-20X (CROSS)

BUY & HOLD ✅""", Signal("ONT", [2.25, 2.38], [2.52, 2.6, 2.67, 2.73, 2.8, 2.88, 2.98], 2.15))


class TestMCVIP(TestSignal):
    def test_1(self):
        self._assert_signal(
            MCVIP, """BTCUSDT LONG 36705-36200
Target 37000-37400-38000-38500
Leverage 10x
Stop 35680""", Signal("BTC", [36705, 36200], [37000, 37400, 38000, 38500], 35680))

    def test_2(self):
        self.assertRaises(
            AssertionError,
            self._assert_signal,
            MCVIP, """ETHUSDT Buy 2580-2626
Targets 2800-3050-3300
Stop 2333""", None)

    def test_3(self):
        coin = None
        try:
            self._assert_signal(
                MCVIP, """Close algo""", None)
        except CloseTradeException as exp:
            coin = exp.coin
        self.assertEqual(coin, "ALGO")

    def test_4(self):
        self._assert_signal(
            MCVIP, """1INCH/USDT ️ Long above 4.0009
Targets: 4.0169 - 4.034- 4.0503 - 4.082- 4.162
Leverage 10x
Stop 3.799""", Signal("1INCH", [4.0009], [4.0169, 4.034, 4.0503, 4.082, 4.162], 3.799))


class TestMVIP(TestSignal):
    def test_1(self):
        self._assert_signal(
            MVIP, """⚡️⚡️ #BNB/USDT⚡️⚡️

Entry Zone :
390,50 - 391,00
Take-Profit Targets:

1) 394,91
2) 410,55
3) 430,10

Leverage ×10

Stop Targets:

1) 312,80""", Signal("BNB", [390.5, 391], [394.91, 410.55, 430.10], 312.8))

    def test_2(self):
        self._assert_signal(
            MVIP, """⚡️⚡️ #CTK/USDT ⚡️⚡️

Entry Zone:
1.500 - 1.501

Take-Profit Targets:
1) 1.560
2) 1.650
3) 1.750

Levrage ×50

Stop Targets:
1) 1.400""", Signal("CTK", [1.5, 1.501], [1.56, 1.65, 1.75], 1.4, 50))

    def test_3(self):
        self.assertRaises(
            AssertionError,
            self._assert_signal,
            MVIP, """⚡️⚡️ #HNT/USDT ⚡️⚡️

Entry Zone:
16,0000 - 16,0700

Take-Profit Targets:

1) 19,2840
2) 24,0700
3) 32,0700

Stop Targets:

1) 15,7486""", None)

    def test_4(self):
        self._assert_signal(MVIP, """⚡️⚡️ #LTC/USDT⚡️⚡️

Entry Zone:
174 - 175

Take-Profit Targets:

1) 176
2) 178

Leverage : ×50

Stop Targets:
1) 170""", Signal("LTC", [174, 175], [176, 178], 170, 50))

    def test_5(self):
        self.assertRaises(AssertionError, self._assert_signal, MVIP, """[In reply to 👑 MVIP 👑]
Close second trade when first tp hit 🎯""", None)

    def test_6(self):
        coin = None
        try:
            self._assert_signal(
                MVIP, """[In reply to 👑 MVIP 👑]
Close #BTC/USDT""", None)
        except CloseTradeException as exp:
            coin = exp.coin
        self.assertEqual(coin, "BTC")

    def test_7(self):
        coin = "UNKNOWN"
        try:
            self._assert_signal(
                MVIP, """🛑 Close all trades  🛑""", None)
        except CloseTradeException as exp:
            coin = exp.coin
        self.assertEqual(coin, None)

    def test_8(self):
        self.assertRaises(AssertionError, self._assert_signal, MVIP, """⚡️⚡️ #LINK/USDT⚡️⚡️

Entry Zone:
22.7 - 22.8

Take-Profit Targets:

1) 23.2
2) 23.7
3) 24.1

Leverage ×10

Stop Targets:
1) 21.4""", Signal("LINK", [0], []))

    def test_9(self):
        self._assert_signal(MVIP, """⚡️⚡️ # ETC / USDT ⚡️⚡️

Entry Zone:
  58.10 - 58.20

Take-Profit Targets:
1) 58.78
2) 59.36
3) 59.94

Leverage×50

Stop Targets:
1) 55.29""", Signal("ETC", [58.1, 58.2], [58.78, 59.36, 59.94], 55.29, 50))

    def test_10(self):
        self._assert_signal(MVIP, """⚡️⚡️ #MKR/USDT⚡️⚡️

Entry Zone:

 2308  - 2310

Take-Profit Targets:

1) 2356
2) 2402
3) 2448

Leverage ×20

Stop Targets:
1) 2194""", Signal("MKR", [2308, 2310], [2356, 2402, 2448], 2194))

    def test_11(self):
        self._assert_signal(MVIP, """Long EGLD/USDT

Entry   84.8 / 83

Targets  94 / 100 / 105 / 112

Stop loss : 80


Leverage cross x10

Exchange : Binance Futures""", Signal("EGLD", [84.8, 83], [94, 100, 105, 112], 80))


class TestTCA(TestSignal):
    def test_1(self):
        self._assert_signal(
            TCA, """Asset: EOS/USDT
Position: #LONG
Entry: 5.850 - 5.950
Targets: 6.000 - 6.100 - 6.300 - 6.500
Stop loss: 5.600
Leverage: 75x""", Signal("EOS", [5.85, 5.95], [6, 6.1, 6.3, 6.5], 5.6, 75))

    def test_2(self):
        self._assert_signal(
            TCA, """Leverage Trading Signal
Pair: BTC/USDT #LONG
Leverage: cross 100x (not more than 3-4% balance)
Targets : 39000 - 39500 - 40000 - 41800
Entry : 38500 - 38700
SL: 37300""", Signal("BTC", [38500, 38700], [39000, 39500, 40000, 41800], 37300, 100))

    def test_3(self):
        coin = None
        try:
            self._assert_signal(
                TCA, """Close position
BTC by 35091
Profit is +300%""", None)
        except CloseTradeException as exp:
            coin = exp.coin
        self.assertEqual(coin, "BTC")

    def test_4(self):
        coin = "UNKNOWN"
        try:
            self._assert_signal(
                TCA, """Closing all positions. Leaving the market""", None)
        except CloseTradeException as exp:
            coin = exp.coin
        self.assertEqual(coin, None)

    def test_5(self):
        coin = "UNKNOWN"
        try:
            self._assert_signal(
                TCA, """Closing eth at entry""", None)
        except CloseTradeException as exp:
            coin = exp.coin
        self.assertEqual(coin, "ETH")

    def test_6(self):
        self._assert_signal(TCA, """P﻿﻿a﻿﻿﻿﻿﻿i﻿﻿﻿﻿﻿﻿﻿r﻿:﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿ ﻿﻿﻿﻿B﻿﻿﻿﻿﻿﻿﻿﻿﻿T﻿﻿﻿﻿C﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿/﻿﻿﻿USDT #LONG
Leverage: cross 100x (not more than 3-4% balance)
Targets : 40300 - 40700 - 41100 - 41500
Entry : around 39800 - 40000
SL: 39200
""", Signal("BTC", [39800, 40000], [40300, 40700, 41100, 41500], 39200, leverage=100))


class TestRM(TestSignal):
    def test_1(self):
        self._assert_signal(
            RM, """⚡️⚡️ #BTC/USDT ⚡️⚡️

Client: Binance Futures
Trade Type: Regular (LONG)
Leverage: Isolated (10.0X)

Entry Zone:
38500 - 38980

Take-Profit Targets:
1) 39265 - 20%
2) 39700 - 20%
3) 40100 - 20%
4) 40500 - 20%
5) 41000 - 20%

Stop Targets:
1) 36430 - 100.0%

Risk level 8/10
Published By:
provided by : @CVIP""",
            Signal("BTC", [38500, 38980], [39265, 39700, 40100, 40500, 41000], 36430))


class TestVIPCS(TestSignal):
    def test_1(self):
        self._assert_signal(
            VIPCS, """➡️ SHORT LINKUSDT | Binance

❇️ Buy: 27.00000000

☑️ Target 1: 22.95000000 (15%)

☑️ Target 2: 18.90000000 (30%)

☑️ Target 3: 14.85000000 (45%)

⛔️ Stoploss: 31.05000000  (-15%)

💫 Leverage : 10x""", Signal("LINK", [27], [22.95, 18.9, 14.85], 31.05))

    def test_2(self):
        self._assert_signal(
            VIPCS, """⚡⚡ #LINK/USDT ⚡⚡
Exchanges: Binance Futures
Signal Type: Regular (Short)
Leverage: Isolated (10.0X)

Entry Targets:
1) 27 ✅

Take-Profit Targets:
1) 24
2) 21.6
3) 18.9
4) 14
5) 11

Stop Targets:
1) 29.7

Published By: @V""", Signal("LINK", [27], [24, 21.6, 18.9, 14, 11], 29.7))

    def test_3(self):
        coin = None
        try:
            self._assert_signal(
                VIPCS, """[In reply to VIPCS]
Close TRB""", None)
        except CloseTradeException as exp:
            coin = exp.coin
        self.assertEqual(coin, "TRB")

    def test_4(self):
        self._assert_signal(
            VIPCS, """➡️ SHORT BTCUSDT | Binance

❇️ Entry : 36700.00000000

☑️ Target 1: 31195.00000000 (15%)

☑️ Target 2: 25690.00000000 (30%)

☑️ Target 3: 20185.00000000 (45%)

⛔️ Stoploss: 42205.00000000  (-15%)

💫 Leverage : 5x - 10x""", Signal("BTC", [36700], [31195, 25690, 20185], 42205))


class TestCEP(TestSignal):
    def test_1(self):
        self._assert_signal(
            CEP, """#ETHUSDT

📍 SHORT

Leverage : 20x

📍Use 2% of Total Account

Buy : 2700 - 2660 - 2630

Sell Targets ::

2600 - 2560 - 2510 - 2460 - 2400 - 2300 - 2200 - 2100

🔻 StopLoss : 2850


#Crypto ✅""", Signal("ETH", [2700, 2660, 2630], [2600, 2560, 2510, 2460, 2400, 2300, 2200, 2100], 2850))


class TestEBS(TestSignal):
    def test_1(self):
        self._assert_signal(
            EBS, """#EXCHANGE: Binance(spot)/ Evolve
Leverage: 50x

 #ETH/USDT

Scalp Setup

Short Entry:
  2679.00

Target 1 - 2666.48
Target 2 - 2648.69

by @CRR""", Signal("ETH", [2679], [2666.48, 2648.69], leverage=100))

    def test_2(self):
        self._assert_signal(
            EBS, """#EXCHANGE: Binance(spot)/ Evolve
Leverage: 32

 #BTC/USDT

Scalp Setup

Short Entry:
  36160

Target 1 - 35959
Target 2 - 35672

by @CTT""", Signal("BTC", [36160], [35959, 35672], leverage=100))

    def test_3(self):
        self._assert_signal(EBS, """#EXCHANGE: Binance(spot)/ Evolve

 #BTC/USDT

Scalp Setup

Short Entry:
  39470

Target 1 - 39284
Target 2 - 38997

by @CRR""", Signal("BTC", [39470], [39284, 38997], leverage=100))


class TestKBV(TestSignal):
    def test_1(self):
        self._assert_signal(
            KBV, """#B&BF

#ONT/USDT ️
#SHORT
Entry LIMIT: 1.0665

SELL:
1.0620 - 1.0580 - 1.0535 - 1.0450 - 1.0240

Leverage - 10x

❗️STOP LOSS : 1.120

by @CRR""", Signal("ONT", [1.0665], [1.062, 1.058, 1.0535, 1.045, 1.024], 1.12))

    def test_2(self):
        self._assert_signal(
            KBV, """#B&BF

#SNX/USDT ️
#SHORT
Entry LIMIT: 11.40

SELL:
11.300 - 11.255 - 11.205 - 11.120
11.890

Leverage - 10x

❗️STOP LOSS : 12$

by @CRR""", Signal("SNX", [11.4], [11.3, 11.255, 11.205, 11.12], 12))

    def test_3(self):
        self._assert_signal(
            KBV, """#B&BF

#BZRX/USDT ️
#LONG
BUY LIMIT: 3000

SELL:
3012 - 3024 - 3036 - 3060 - 3120

Leverage - 10x

❗️STOP LOSS : 2850.

by @CRR""", Signal("BZRX", [3000], [3012, 3024, 3036, 3060, 3120], 2850))


class TestBVIP(TestSignal):
    def test_1(self):
        self._assert_signal(
            BVIP, """1INCHUSDT LONG 0.324-0.30
Targets 0.348-0.365
Leverage 4x
Stop 0.292

by @CRR""", Signal("1INCH", [0.324, 0.3], [0.348, 0.365], 0.292))

    def test_2(self):
        self._assert_signal(
            BVIP, """LTCUSDT LONG 182-176
Targets 186-191-196-205
Leverage 15x
stop 162

by @CRR""", Signal("LTC", [182, 176], [186, 191, 196, 205], 162))

    def test_3(self):
        self._assert_signal(BVIP, """Long LTC/USDT

Entry  131.4 / 129.7
Targets 134-  137- 140- 143
Stop loss : 122
Leverage 10x

@TB

by @CRR""", Signal("LTC", [131.4, 129.7], [134, 137, 140, 143], 122))

    def test_4(self):
        self._assert_signal(BVIP, """BTC / USDT

Long

Buying:- 34300$-34700$!

Target 35500-36000-38000!

StopLoss:- 33200

by @CRR""", Signal("BTC", [34300, 34700], [35500, 36000, 38000], 33200))


class TestPBF(TestSignal):
    def test_1(self):
        self._assert_signal(
            PBF, """Binance Future
OCEANUSDT ❗️LONG
Entry Price       0,582800
Leverage :  cross (×20)
Target :  0,592709
Stop loss :  0,57137
Capital invested :  2%

by @CRR""", Signal("OCEAN", [0.5828], [0.592709], 0.57137))


class TestFXVIP(TestSignal):
    def test_1(self):
        self._assert_signal(
            FXVIP, """Binance Future
DGBUSDT ❗️LONG
Entry Price       0,062400
Leverage :  cross (×20)
Target :  0,063649
Stop loss :  UPDATE
Capital invested :  2%

by @CRR""", Signal("DGB", [0.0624], [0.063649], None))

    def test_2(self):
        self._assert_signal(
            FXVIP, """#ICP/USDT #LONG
(BINANCE FUTURES )
BUY : 82$- 88.2$

TAKE PROFIT:
TARGET 1 : 93.00$
TARGET 2 : 95.50$
TARGET 3 : 98.00$
TARGET 4 : 101.0$
TARGET 5 : 104.0$
TARGET 6 : 108.0$

❗️STOP LOSS :80$

Use 2% Fund Only ❗️

LEV :  10X-20X (CROSS)

BUY & HOLD ✅

by @CRR""", Signal("ICP", [82, 88.2], [93, 95.5, 98, 101, 104, 108], 80))

    def test_3(self):
        self._assert_signal(
            FXVIP, """1INCH/USDT ️ Long above 14.024
Targets: 14.074 - 14.129- 14.199 - 14.31 - 14.6
Leverage 10x
Stop 13.324

by @CRR""", Signal("1INCH", [14.024], [14.074, 14.129, 14.199, 14.31, 14.6], 13.324))

    def test_4(self):
        self._assert_signal(
            FXVIP, """📊 FUTURES (BINANCE)

#BELUSDT

LONG Below : 1.65

MAX 👉5x-7x LEVERAGE Hold

TAKE PROFIT: 1.70|1.76|1.85+

by @CRR""", Signal("BEL", [1.65], [1.7, 1.76, 1.85]))

    def test_5(self):
        self._assert_signal(
            FXVIP, """AAVEUSDT | LONG |

ENTRY 305 - 285

TARGET 395 - 450 - 530

STOP LOSS 254

LEVERAGE 3–10X

by @CRR""", Signal("AAVE", [305, 285], [395, 450, 530], 254))

    def test_6(self):
        self._assert_signal(FXVIP, """#ALGO/USDT
Exchanges: Binance
Signal Type: Regular (Long)

Entry Zone: 0.8152 - 0.8685

Take-Profit Targets:
1) 0.8879 - 11.111%
2) 0.9270 - 11.111%
3) 0.9660 - 11.111%
4) 1.0117 - 11.111%
5) 1.0546 - 11.111%
6) 1.1735 - 11.111%
7) 1.249 - 11.111%
8) 1.329 - 11.111%
9) 1.4138 - 11.111%

Stop Targets:
1) 0.7756

Trailing Configuration:
Stop: Breakeven -
  Trigger: Target (2)
""", Signal("ALGO", [0.8152, 0.8685], [0.8879, 0.927, 0.966, 1.0117, 1.0546, 1.1735, 1.249, 1.329, 1.4138], 0.7756))


class TestHBTCV(TestSignal):
    def test_1(self):
        self._assert_signal(
            HBTCV, """⚡️⚡️ #ETH/USDT ⚡️⚡️

Client: Binance Futures
Trade Type: Regular (SHORT)
Leverage: Isolated (5.0X)

Entry Zone:
2460- 2478

Take-Profit Targets:
1) 2430 - 20%
2) 2409- 20%
3) 2380 - 20%
4) 2345 - 20%
5) 2250- 20%

Stop Targets:
1) 2630 - 100.0%

by @CRR""", Signal("ETH", [2460, 2478], [2430, 2409, 2380, 2345, 2250], 2630))

    def test_2(self):
        self.assertRaises(
            AssertionError,
            self._assert_signal,
            HBTCV,
            """⚡️⚡️ #ETH/USDT ⚡️⚡️

Client: Binance Futures
Trade Type: Regular (SHORT)
Leverage: Isolated (10.0X)

Entry Zone:
2460- 2478

Take-Profit Targets:
1) 2430 - 20%✅
2) 2409- 20%✅
3) 2380 - 20%✅😎
4) 2345 - 20%
5) 2250- 20%

Stop Targets:
1) 2630 - 100.0%

by @CRR""", None)

    def test_3(self):
        self.assertRaises(
            AssertionError,
            self._assert_signal,
            HBTCV,
            """#ETH USDT

📍 SHORT

Leverage : 10x 20x (cross)

📍Use 2% of Total Account

ENTRY  : 2700 - 2660 - 2630

 Targets ::

2600✅ - 2560✅😎 - 2510 - 2460 - 2400 - 2300 - 2200 - 2100

🔻 StopLoss : 2900 (daily close)

by @CRR""", None)

    def test_4(self):
        self._assert_signal(
            HBTCV, """#ETH USDT

📍 SHORT

Leverage : 10x 20x (cross)

📍Use 2% of Total Account

ENTRY  : 2700 - 2660 - 2630

 Targets ::

2600 - 2560 - 2510 - 2460 - 2400 - 2300 - 2200 - 2100

🔻 StopLoss : 2900 (daily close)

by @CRR""", Signal("ETH", [2700, 2660, 2630], [2600, 2560, 2510, 2460, 2400, 2300, 2200, 2100], 2900))

    def test_5(self):
        self._assert_signal(
            HBTCV, """#BINANCE FUTURES $LTC


#LTC/USDT (Long)

🛒Entry 1 - 159.80 (30%)

🛒Entry 2 - 153 (30%)

🛒Entry 3 - 147 (40%)

🎯Targets - 164.5 - 170 - 188 - 205 - 230

Stoploss - 145

Leverage - 3-4x

by @CRR""", Signal("LTC", [159.8, 153, 147], [164.5, 170, 188, 205, 230], 145))

    def test_6(self):
        self.assertRaises(
            AssertionError,
            self._assert_signal,
            HBTCV, """#BINANCE FUTURES $LTC


#LTC/USDT (Long)

🛒Entry 1 - 159.80 (30%)

🛒Entry 2 - 153 (30%)

🛒Entry 3 - 147 (40%)

🎯Targets - 164.5 ✅😎- 170 - 188 - 205 - 230

Stoploss - 145  (daily close)

Leverage - 3-4x

by @CRR""", None)


class TestCY(TestSignal):
    def test_1(self):
        self._assert_signal(CY, """ICP/USDT
Leverage 10X
Buy 57 to 58
Sell  63
Stop 51

by @CRR""", Signal("ICP", [57, 58], [63], 51, 10))

    def test_2(self):
        self._assert_signal(CY, """MTL/USDT
Leverage 15X
Buy 2.0510 to 2.1070
Sell  2.20
Stop 1.95

by @CRR""", Signal("MTL", [2.051, 2.107], [2.2], 1.95, 15))

    def test_3(self):
        coin = None
        try:
            self._assert_signal(
                CY, """Stop DOGEUSDT

by @CRR""", None)
        except CloseTradeException as exp:
            coin = exp.coin
        self.assertEqual(coin, "DOGE")

    def test_4(self):
        self._assert_signal(CY, """ALICE/USDT
Leverage 20X
Buy   3.90 to 4.05
Target 1  4.20
Target 2.  4.50
Stop  3.75

by @CRR""", Signal("ALICE", [3.9, 4.05], [4.2, 4.5], 3.75, 20))

    def test_5(self):
        self._assert_signal(CY, """SNX/USDT
Leverage 20X
Sell  11.90 TO 12
Target 1  11.60
Target 2  10
Target 3   9.50
Stop  12.30

Small margin suggested

by @CRR""", Signal("SNX", [11.9, 12], [11.6, 10, 9.5], 12.3))


class TestKCE(TestSignal):
    def test_1(self):
        self._assert_signal(KCE, """BZRX/USDT x10 “SHORT” signal

Entry : 0.303 - 0.305

Target : 0.285$ - 0.28$

No stoploss

by @CRR""", Signal("BZRX", [0.303, 0.305], [0.285, 0.28]))

    def test_2(self):
        self._assert_signal(KCE, """AKRO/USDT x10

Entry : 0.022$ - 0.0225$

Target : 0.024$ - 0.026$

SL : 0.02$

Enjoy!!

by @CRR""", Signal("AKRO", [0.022, 0.0225], [0.024, 0.026], 0.02))

    def test_3(self):
        self._assert_signal(KCE, """1INCH/USDT buy setup : 0.327$ - 0.33$ x10

Target : 0.34$ - 0.36$ - 0.38$

SL : 0.3$

by @CRR""", Signal("1INCH", [0.327, 0.33], [0.34, 0.36, 0.38], 0.3))

    def test_4(self):
        self._assert_signal(KCE, """NKN/USDT x10

Now : 0.33$

Target 1 : 0.35$
Target 2 : 0.38$
Target 3 : 0.4$

Enjoy!!

by @CRR""", Signal("NKN", [0.33], [0.35, 0.38, 0.4]))

    def test_5(self):
        self._assert_signal(KCE, """BTS/USDT x10 “SHORT”

Now : 0.0555$

Target : 0.052$ - 0.05$

0.06$ can be stop

by @CRR""", Signal("BTS", [0.0555], [0.052, 0.05], 0.06))

    def test_6(self):
        self._assert_signal(KCE, """TOMO/USDT 10x

Now : 2.68$

Target 1 : 2.75$
Target 2 : 2.8$
Target 3 : 3$

Enjoy!!

by @CRR""", Signal("TOMO", [2.68], [2.75, 2.8, 3]))


class TestRWS(TestSignal):
    def test_1(self):
        self._assert_signal(RWS, """Enter Long 📈

ETH/USDT 2420

Leverage x5

Targets :

🎯 2470
🎯 2515
🎯 2580
🎯 2650

Stop loss 🔴 2364

by @CRR""", Signal("ETH", [2420], [2470, 2515, 2580, 2650], 2364, 5))

    def test_2(self):
        self._assert_signal(RWS, """⚡️⚡️ #ETH/USDT ⚡️⚡️
Exchanges: Binance Futures
Signal Type: Regular (Short)
Leverage: Isolated (10.0X)

Entry Targets:
1) 2370 - 50.0% ✅
2) 2400 - 50.0% ✅

Take-Profit Targets:
1) 2310
2) 2275
3) 2210
4) 2110
5) 1990

Stop Targets:
1) 2411

Published By: @Adam

by @CRR""", Signal("ETH", [2370], [2310, 2275, 2210, 2110, 1990], 2411, 10))

    def test_3(self):
        coin = None
        try:
            self._assert_signal(
                RWS, """[In reply to RWS]
Close ETH/USDT

by @CRR""", None)
        except CloseTradeException as exp:
            coin = exp.coin
        self.assertEqual(coin, "ETH")


class TestSS(TestSignal):
    def test_1(self):
        self._assert_signal(SS, """#BTCUSDT

#SHORT 35100-37260

Close 33660 31500 29700 27000

Stop 37980

Lev 3X""", Signal("BTC", [35100, 37260], [33660, 31500, 29700, 27000], 37980))


class TestSLVIP(TestSignal):
    def test_1(self):
        self._assert_signal(SLVIP, """#BNB_USDT Scalp Long!!

 Entry Zone:350 & 320

Sell Zone:353-357-365-380-400

StopLoss : 1H Candle Close Under 300

Lev: Cross With 50-75X

Exchange : Binance Futures

by @CRR""", Signal("BNB", [350, 320], [353, 357, 365, 380, 400], 300, 75))

    def test_2(self):
        self._assert_signal(
            SLVIP, """[ Photo ]
https://www.tradingview.com/

#BTC/USDT Open small Short postion here ‼️

OPEN SHORT:- 33760-33890-34090

STOP 🛑 :- 34800

TARGET:-33600-33500-33300-33000-32700-32500-32100-31800-31700 BELOW ‼️

LEV :- 2X/3X

USE 2% FUND ‼️‼️

by @CRR""", Signal("BTC", [33760, 33890, 34090],
                   [33600, 33500, 33300, 33000, 32700, 32500, 32100, 31800, 31700], 34800, 5))


class TestCCC(TestSignal):
    def test_1(self):
        self._assert_signal(CCC, """#BINANCEFUTURES $LTC

https://www.tradingview.com/

#LTC/USDT (Long)

🛒Entry 1 - 159.80 (30%) (Filled)

🛒Entry 2 - 153 (30%)

🛒Entry 3 - 147 (40%)

🎯Targets - 164.5 - 170 - 188 - 205 - 230

Stoploss - 145

Leverage - 3-4x

@Forex_Tradings)""", Signal("LTC", [159.8, 153, 147], [164.5, 170, 188, 205, 230], 145))

    def test_2(self):
        self._assert_signal(CCC, """[ Photo ]
BTC scalp short

Entry 35200-36000

stop 36300

Leverage 3x

Target 33500

#CCC

by @CRR""", Signal("BTC", [35200, 36000], [33500], 36300))

    def test_3(self):
        self._assert_signal(CCC, """[ Photo ]
DOGE short 😱

Entry now between 0.303 - 0.31

stop 🛑 close 4hr above 0.313 or 0.33 manually

Targets 0.295 - 0.267 - 0.22 🎯

Leverage 3x

#CCC

by @CRR""", Signal("DOGE", [0.303, 0.31], [0.295, 0.267, 0.22], 0.33))

    def test_4(self):
        self._assert_signal(CCC, """[ Photo ]
THETA short

Entry between cmp 8.8 USDT to 9.5 USDT

stop 🛑 if close 4hr above 10$

leverage up to 3x

Targets are 🎯 8.4 - 8 - 7.7 - 6.3 and bonus target wick down to 3.1 to 4.5 zone

#CCC bearish season hunter

by @CRR""", Signal("THETA", [8.8, 9.5], [8.4, 8, 7.7, 6.3, 3.1], 10))

    def test_5(self):
        self._assert_signal(CCC, """[ Photo ]
#BNB

🛒Entry 1 - 299 - CMP (30%)

🛒Entry 2 - 285 (30%)

🛒Entry 3 - 275 (40%)

🎯Targets - 310 - 322 - 340 - 365 - 400

Stoploss - 265

Leverage  - 2x - 3x

#CCC

by @CRR""", Signal("BNB", [299, 285, 275], [310, 322, 340, 365, 400], 265, 5))


class TestKSP(TestSignal):
    def test_1(self):
        self._assert_signal(KSP, """⚡️⚡️ #BTC/USDT ⚡️⚡️
Exchanges: Binance Futures
Signal Type: Regular (Long)
Leverage: Isolated (5.0X)

Entry Targets:
39477.31 - 37555.60

Take-Profit Targets:
1) 41131.68 - 10.0%
2) 43082.27 - 25.0%
3) 44924.49 - 40.0%
4) 47200.18 - 10.0%
5) 51209.72 - 5.0%
6) 53485.41 - 5.0%
7) 56000.00 - 5.0%

Stop Targets:
1) 35171.54""", Signal("BTC", [39477.31, 37555.6],
                       [41131.68, 43082.27, 44924.49, 47200.18, 51209.72, 53485.41, 56000], 35171.54))


class TestBFP2(TestSignal):
    def test_1(self):
        self._assert_signal(BFP2, """Long/Buy #1INCHUSDT $0.0070
Target $0.0077-$0.0085-$0.0099+
Stop Loss Use Below $0.0055
Leverage Use Only 3x-5x ✈️

by @CRR""", Signal("1INCH", [0.007], [0.0077, 0.0085, 0.0099], 0.0055))

    def test_2(self):
        self._assert_signal(BFP2, """Risky Signal For Leverage Traders
#ICPUSDT Long/Buy Oportunity
Buy Below Only $29.00
Target $30.50-$31.70-$33.00-$35.00+
Stop Loss Use Must $28.00
Leverage Use Only 3x-5x Maximum

by @CRR""", Signal("ICP", [29], [30.5, 31.7, 33, 35], 28))

    def test_3(self):
        self._assert_signal(BFP2, """#1INCH Long Now Below $300
Target $310-$325-$350+
Stop Loss Use Must At $280
Leverage Only 3x-5x Maximum ✈️

by @CRR""", Signal("1INCH", [300], [310, 325, 350], 280))


class TestVIPBB(TestSignal):
    def test_1(self):
        s = Signal("BTC", [37.1, 36.3], [38, 39, 41.4, 42.2], 34.4, leverage=25)
        self._assert_signal(VIPBB, """#BTC/USDT
LONG
Buy Setup:  37.1-36.3

SELL:
38K - 39K - 41.4 - 42.2K

LEV : 5X - 10X - 25X

❗️STOP LOSS : 34.4

by @CRR""", s)
        s.correct(36000)
        self.assertEqual(s.entries, [36300, 37100])
        self.assertEqual(s.targets, [37983, 38990, 41376, 42192])
        self.assertEqual(s.sl, 34400)
        self.assertAlmostEqual(s.fraction, 0.00724210526)

    def test_2(self):
        self._assert_signal(VIPBB, """#BTC/USDT
#LONG
BUY : 39850 - 40300

Take-Profit Targets:
40900 - 41300 - 41600 - 42000 - 42300

LEV : 5X - 10X - 20X

❗️STOP LOSS : 38600$

by @CRR""", Signal("BTC", [39850, 40300], [40900, 41300, 41600, 42000, 42300], 38600))

    def test_3(self):
        self._assert_signal(VIPBB, """#B&BF

#ADA/USDT ️
#LONG
Entry : 1.34$

SELL:
1.38$  - 1.43$ - 1.50$ - 1.55$ - 1.70$

Leverage - 10x

❗️STOP LOSS : 1.20$

by @CRR""", Signal("ADA", [1.34], [1.38, 1.43, 1.5, 1.55, 1.7], 1.2))

    def test_4(self):
        self._assert_signal(VIPBB, """#DENT/USDT ️
Call Type- LONG
Buy Range LIMIT: 2785

Targets:
2795 - 2805 - 2820 - 2840 - 2900

Leverage : 5X - 10x

❗️StopLoss : 2600""", Signal("DENT", [2785], [2795, 2805, 2820, 2840, 2900], 2600))

    def test_5(self):
        self._assert_signal(VIPBB, """🔔Coin Name: $ALICE/USDT🔔
📉 Call Type: LONG
**🟢 Buy Limit: 14.30$

🎯 Targets:
14.525  - 14.580 - 14.640 - 14.750
15.045

⚡ Leverage : 5X - 10x

🚫️ Stoploss : 13$**""", Signal("ALICE", [14.3], [14.525, 14.58, 14.64, 14.75], 13))


class TestPVIP(TestSignal):
    def test_1(self):
        self._assert_signal(PVIP, """#Bybit Call

ETH-USDT

BUY LONG: 2460-2480$

LEVERAGE:4x

TARGET 1: 2600$
TARGET 2: 2780$
TARGET 3: 2900$

Stop-loss: 2300$

Use 5-6% Balance)

by @CRR""", Signal("ETH", [2460, 2480], [2600, 2780, 2900], 2300, 5))


class TestPHVIP(TestSignal):
    def test_1(self):
        self._assert_signal(PHVIP, """⚡️⚡️ #ADA/USDT ⚡️⚡️
Exchanges: Binance Futures
Signal Type: Regular (Long)
Leverage: Isolated (5.0X)

Entry Targets:
1.7332 - 1.6057

Take-Profit Targets:
1) 1.8380 - 10.0%
2) 1.9514 - 25.0%
3) 2.1134 - 40.0%
4) 2.3241 - 10.0%
5) 2.5132 - 5.0%
6) 2.6750 - 5.0%
7) 2.8319 - 5.0%

Stop Targets:
1) 1.4490

by @CRR""", Signal("ADA", [1.7332, 1.6057], [1.838, 1.9514, 2.1134, 2.3241, 2.5132, 2.675, 2.8319], 1.449, leverage=5))


class TestCC(TestSignal):
    def test_1(self):
        self._assert_signal(CC, """[ Photo ]
CCS

📈 LONG #ETHUSDT 5X

Entry: 2550 - 2560

TP 1: 2620
TP 2: 2720
TP 3: 2860

S/L: 2450""", Signal("ETH", [2550, 2560], [2620, 2720, 2860], 2450))

    def test_2(self):
        self._assert_signal(CC, """CCS

📈 LONG #FLMUSDT 10X

Entry: now 0.545 🚀

TP 1: 0.573
TP 2: 0.602
TP 3: 0.645

S/L: 0.5200""", Signal("FLM", [0.545], [0.573, 0.602, 0.645], 0.52))


class TestC(TestSignal):
    def test_1(self):
        coin = None
        try:
            self._assert_signal(
                C, """[In reply to Crypto #CRR]
Close BTCUSDT

by @CRR""", None)
        except CloseTradeException as exp:
            coin = exp.coin
        self.assertEqual(coin, "BTC")

    def test_2(self):
        self._assert_signal(C,  """LINK/USDT
Buy 20.1-19
Targets 21.94-24.5-26.6
Leverage 5x
Stop 17.5""", Signal("LINK", [20.1, 19], [21.94, 24.5, 26.6], 17.5, 20))


class TestYCP(TestSignal):
    def test_1(self):
        self._assert_signal(YCP, """Long #IOSTUSDT

Risk level - High

Entry Zone: 0.0280-0.0295

Targets: 0.031-0.034-0.037-0.042-0.045

Leverage - 3x strictly

Put only 5% of your portfolio in this trade

Close: You may keep closing 10-15% of your open positions at each target.

Overall stop-loss - Overall stoploss at 0.025. You may move position stop-loss to trade entry price

Current rate - 0.0292""", Signal("IOST", [0.028, 0.0295], [0.031, 0.034, 0.037, 0.042, 0.045], 0.025, 5))

    def test_2(self):
        coin = None
        try:
            self._assert_signal(YCP, """Cancel #BTCUSDT""", None)
        except CloseTradeException as exp:
            coin = exp.coin
        self.assertEqual(coin, "BTC")


class TestLVIP(TestSignal):
    def test_1(self):
        self._assert_signal(LVIP, """ICXUSDT  IN 4 HOURS 👀👀‼️

#ICX/USDT ON #BINANCE

BUY :- 0.98-0.99-1.0138

TARGET:1.03-1.07-1.09-1.13-1.18-1.21-1.25-1.29++

STOP 🛑:- 0.91

LEV :- 2X/3X

USE 1% FUND RISKY CALL‼️

by @CRR""", Signal("ICX", [0.98, 0.99, 1.0138], [1.03, 1.07, 1.09, 1.13, 1.18, 1.21, 1.25, 1.29], 0.91, 10))

    def test_2(self):
        self._assert_signal(LVIP, """https://www.tradingview.com/

#DOT/USDT‼️‼️

#DOT/USDT 👀👀

BUY :- 22-23-24.09

TARGET:-25.20-25.50-25.90-26.30-26.90++

STOP 🛑:-20

LEV :- 2X

PLACE ORDER .‼️..USE 3%-5% FUND 👀

by @CRR""", Signal("DOT", [22, 23, 24.09], [25.2, 25.5, 25.9, 26.3, 26.9], 20, 10))

    def test_3(self):
        self._assert_signal(LVIP, """#AVAX/USDT  LONG  SPOT & FUTURES 🧐🧐

BUY :- 15.05-15.15-15.372

TARGET:15.69-15.90-16.20-16.70-17.20++‼️

LEV :- 3X

STOP 🛑:- 14.09

SWING CALL BUY WITH 5% Fund and HOLD IT.. you can buy also in spot

by @CRR""", Signal("AVAX", [15.05, 15.15, 15.372], [15.69, 15.9, 16.2, 16.7, 17.2], 14.09, 10))

    def test_4(self):
        self._assert_signal(LVIP, """#BINANCE FUTURES  CALL PLACE ORDER 👇👇

PLACE ORDER‼️‼️‼️👇

1INCHUSDT SHORT 2057-2062-2070

STOP LOSS:- 2110

TARGET:-2040-2030-2020-2000-1980-1960 ++

LEV :- 5X

RISKY 7/10👆‼️

Safe traders use 2X-3X  only with 1% fund only  wait for Order ..  ‼️

by @CRR""", Signal("1INCH", [2057, 2062, 2070], [2040, 2030, 2020, 2000, 1980, 1960], 2110, 10))

    def test_5(self):
        self._assert_signal(LVIP, """#BINANCE FUTURES CALL 👇👇

#ETCUSDT LONG :- 54-55-57.31

TARGET:-59-61-63-65-67-69-71++

LEV :- 3X

SL:- 52

by @CRR""", Signal("ETC", [54, 55, 57.31], [59, 61, 63, 65, 67, 69, 71], 52, 10))

    def test_6(self):
        self._assert_signal(LVIP, """#SAND/USDT ON FUTURE

BUY :- 0.60500-0.61000

TARGET :-0.61500-0.6200-0.6300-0.64000-0.65000

STOP 🛑:- 0.5500

USE 5% FUND ONLY ‼️‼️

by @CRR""", Signal("SAND", [0.605, 0.61], [0.615, 0.62, 0.63, 0.64, 0.65], 0.55))

    def test_7(self):
        self._assert_signal(LVIP, """#XRP/USDT SHORT

0.7105-0.7150-0.7230

STOP 🛑:- 0.7480

LEV :- 5X

TARGET:-0.7020-0.6970-0.6899-0.6740-0.6690-0.6610-0.6550 BELOW

USE 2% FUND ‼️

by @CRR""", Signal("XRP", [0.7105, 0.715, 0.723], [0.702, 0.697, 0.6899, 0.674, 0.669, 0.661, 0.655], 0.748))


class TestVIPCC(TestSignal):
    def test_1(self):
        self._assert_signal(
            VIPCC, """#AAVEUSDT

Short : Below 205.27

Leverage : 10x

Take Profit : 204.66 - 203.63 - 202,6 - 201.37 - 199.73

StopLoss : 220.07

Signal by @BSF

⚠️ Don't buy early. Open position when the market price touches the ENTRY POINT ⚠️""",
            Signal("AAVE", [205.27], [204.66, 203.63, 202.6, 201.37, 199.73], 220.07))

    def test_2(self):
        self.assertRaises(
            CloseTradeException,
            self._assert_signal,
            VIPCC, "close", None
        )

    def test_3(self):
        self._assert_signal(VIPCC, """#QTUMUSDT

Short : 6.320 (Around)

Leverage : 30x (4% of Total capital)

Take Profit :
6.200 - 6.100 - 6.000
5.790 - 5.560 - 5.345 - 4.990 - 4.550

StopLoss : 6.810

Signal by @CC""", Signal("QTUM", [6.32], [6.2, 6.1, 6.0], 6.81))

    def test_4(self):
        self._assert_signal(VIPCC, """#AKRO/USDT
#LONG

ENTRY : Below 2835

LEVERAGE : 4x

TARGET 1 : 2898
TARGET 2 : 2950
TARGET 3 : 3010
TARGET 4 : 3100
TARGET 5 : 3250

STOP LOSS : 2600

Signal by @CC""", Signal("AKRO", [2835], [2898, 2950, 3010, 3100, 3250], 2600))

    def test_5(self):
        self._assert_signal(VIPCC, """#KEEP/USDT
#LONG

ENTRY : Below 0.3530

LEVERAGE : 5x - 10x

TARGET 1 : 0.3645
TARGET 2 : 0.3740
TARGET 3 : 0.3850
TARGET 4 : 0.4000
TARGET 5 : 0.4200

Signal by @CryptoCrownTM""", Signal("KEEP", [0.353], [0.3645, 0.374, 0.385, 0.4, 0.42]))


class TestTVIPAW(TestSignal):
    def test_1(self):
        s = Signal("ICP", [48.18], [47.4, 46.2, 44.5, 42, 40], 50)
        s.correct(48.5)
        self.assertEqual(s.targets, [47.4078, 46.212, 44.517, 42.025, 40.02])
        s.targets = [47.4, 46.2, 44.5, 42, 40]
        self._assert_signal(TVIPAW, """ICP/USDT SHORT 🛑
Leverage 20x
Entries 48.18
Target 1 47.4
Target 2 46.2
Target 3 44.5
Target 4 42
Target 5 40

SL 50

TTP 🎾""", s)
        self.assertAlmostEqual(s.risk_reward, 4.49, places=2)

    def test_2(self):
        self._assert_signal(TVIPAW, """ICP/USDT LONG ✳️
Leverage 20x
Entries 48.0
Target1 48.7
Target2 49
Target3 51.5
Target4 55
Target5 60
SL 45""", Signal("ICP", [48], [48.7, 49, 51.5, 55, 60], 45))

    def test_3(self):
        self._assert_signal(TVIPAW, """SAND/USDT SHORT 🛑
Leverage 20x
Entries 0.412
Target 1 .405
Target 2 0.395
Target 3 0.38
Target 4 0.36
Target 5 0.3

SL 0.434""", Signal("SAND", [0.412], [0.405, 0.395, 0.38, 0.36, 0.3], 0.434))

    def test_4(self):
        self._assert_signal(TVIPAW, """AXS/USDT SHORT 🛑
Leverage 20x
Entries 24.4
Target 1 24.0
Target 2 23.4
Target 3 22.5
Target 4 20
Target 5 15
""", Signal("AXS", [24.4], [24, 23.4, 22.5, 20, 15]))


class TestVIPBS(TestSignal):
    def test_1(self):
        self._assert_signal(VIPBS, """#btc long  use 5lev to 20lev

Buy : 34400

Sell : 34900 -35200-35700

Sl : no ....33000""", Signal("BTC", [34400], [34900, 35200, 35700], 33000))

    def test_2(self):
        self._assert_signal(VIPBS, """📊 FUTURES (BINANCE)

#CVCUSDT

LONG Below : 0.30000

Target 0.30600-0.31000-0.31500

MAX 👉3x-20x LEVERAGE Hold""", Signal("CVC", [0.3], [0.306, 0.31, 0.315]))


class TestJPC(TestSignal):
    def test_1(self):
        self._assert_signal(JPC, """#BNBUSDT

LONG ENTRY @299 OR BELOW

TP1- 306
TP2- 311.5
TP3- 317.7

STOPLOSS 288.7""", Signal("BNB", [299], [306, 311.5, 317.7], 288.7))

    def test_2(self):
        self._assert_signal(JPC, """#BTCUSDT

LONG NOW BELOW 35000-35050


TP1- 35250-
TP2- 35440
TP3- 35700

STOPLOSS 34570""", Signal("BTC", [35000, 35050], [35250, 35440, 35700], 34570))

    def test_3(self):
        self._assert_signal(JPC, """#BTCUSDT

SHORT 33100-33150

TARGET 32700-32360-32000


STOPLOSS 33870""", Signal("BTC", [33100, 33150], [32700, 32360, 32000], 33870))

    def test_4(self):
        self._assert_signal(JPC, """#1INCHUSDT

LONG ENTRY

2.468-2.472

TP1- 2.4990
TP2- 2.5350
TP3- 2.5790

STOP-LOSS 2.400""", Signal("1INCH", [2.468, 2.472], [2.499, 2.535, 2.579], 2.4))

    def test_5(self):
        self._assert_signal(JPC, """#ETHUSDT

LONG  ENTRY 2330 OR BELOW


TP1-2367
TP2-2401
TP3-2455

STOPLOSS 2250""", Signal("ETH", [2330], [2367, 2401, 2455], 2250))

    def test_6(self):
        self._assert_signal(JPC, """#TLMUSDT

ENTRY RANGE 0.3000-0.3020

TP1- 0.3100

TP2- 0.3200

TP3- 0.3300

STOPLOSS 0.2850""", Signal("TLM", [0.3, 0.302], [0.31, 0.32, 0.33], 0.285))

    def test_7(self):
        self._assert_signal(JPC, """__#**LITUSDT**

LONG ENTRY 3.70-3.75

TP1- 3.82

TP2- 3.88

TP3-3.97

STOPLOSS 3.49__""", Signal("LIT", [3.7, 3.75], [3.82, 3.88, 3.97], 3.49))

    def test_8(self):
        self._assert_signal(JPC, """__#**BZRXUSDT**
0.234-0.2360

TP1- 0.2450

TP2- 0.2520

TP3- 0.2600

SL- 0.2180__""", Signal("BZRX", [0.234, 0.2360], [0.245, 0.252, 0.26], 0.218))


class TestW(TestSignal):
    def test_1(self):
        self._assert_signal(W, """$ETH SHORT

Sell: 2220 - 2240
Target: 2175 - 2001 - 1801
Stoploss: 2301

https://www.tradingview.com/""", Signal("ETH", [2220, 2240], [2175, 2001, 1801], 2301))

    def test_2(self):
        self._assert_signal(W, """$AXS

Long above: 12$ ( It will enter discovery zone)
Target: 14$ - 18$ - 25$
Stopls; 10$

https://www.tradingview.com/""", Signal("AXS", [12], [14, 18, 25], 10))

    def test_3(self):
        self._assert_signal(W, """OGN - USDT

Long: 0.75 - 0.77
Target: 0.80 - 0.95 - 1.20
Stopls: 0.69

https://www.tradingview.com/x/

by @CRR""", Signal("OGN", [0.75, 0.77], [0.8, 0.95, 1.2], 0.69))


class TestJMP(TestSignal):
    def test_1(self):
        self._assert_signal(JMP, """[ Photo ]
COIN: $ETH/USDT
EXCHANGE: Binance
Lev.: 5-10x
==============
Short term, higher leverage entry for ETH. About to break its inverted H&S.

BUY: 2217 - 2330

SELL: 2350 - 2380 - 2410 - 2480 - 2550 - 2650 - 2800 - 3000 - 3350

SL: Below 2043
==============
Big Pumps™

by @CRR""", Signal("ETH", [2217, 2330], [2350, 2380, 2410, 2480, 2550, 2650, 2800, 3000, 3350], 2043))


class TestBK(TestSignal):
    def test_1(self):
        self._assert_signal(BK, """[ Photo ]
📍SIGNAL ID: 0329📍
COIN: $ONT/USDT (3-5x)
Direction: LONG📈
➖➖➖➖➖➖➖
Another short term catch of ONT for the books. Enjoy killers😘

ENTRY: 0.672 - 0.705
OTE: 0.687

TARGETS
Short Term: 0.72 - 0.74 - 0.77 - 0.81
Mid Term: 0.86 - 0.92 - 1.00 - 1.09

STOP LOSS: 0.627
➖➖➖➖➖➖➖
This message cannot be forwarded or replicated
- BK®""", Signal("ONT", [0.672, 0.705], [0.72, 0.74, 0.77, 0.81, 0.86, 0.92, 1.00, 1.09], 0.627))


class TestE(TestSignal):
    def test_1(self):
        self._assert_signal(E, """#rlc/usdt #long
4X Lev

Long Zone: 2.70 _ 2.84
Target: 3.60 +
SL: 2.67""", Signal("RLC", [2.7, 2.84], [3.6], 2.67))

    def test_2(self):
        self._assert_signal(E, """#axs/usdt #short
3x Lev
Short Zone : 9.13 _ 10.0
Target: 7.8
Sl: 10.1""", Signal("AXS", [9.13, 10], [7.8], 10.1))

    def test_3(self):
        self._assert_signal(E, """#ocean/usdt #long
4x Lev
Long Zone: .390 _ .413
Target: .500
SL: .38""", Signal("OCEAN", [0.39, 0.413], [0.5], 0.38))


class TestAS(TestSignal):
    def test_1(self):
        self._assert_signal(AS, """⚡️⚡️ #ETH/USDT ⚡️⚡️
Exchanges: Binance Futures
Signal Type: Regular (Short)
Leverage: Cross (25.0X)

Entry Targets:
1) 2265 - 100.0% ✅

Take-Profit Targets:
1) 2201 - 33.4%
2) 2040 - 33.3%
3) 1788 - 33.3%

Stop Targets:
1) 2400""", Signal("ETH", [2265], [2201, 2040, 1788], 2400, 25))

    def test_2(self):
        self._assert_signal(AS, """Sell ETH/USDT

Entry Price: 2265
Stop Loss: 2300
Take Profit: 2201 - 2040 - 1788
Leverage: cross x25""", Signal("ETH", [2265], [2201, 2040, 1788], 2300, 25))

    def test_3(self):
        self.assertRaises(
            AssertionError,
            self._assert_signal,
            AS, """⚡️⚡️ #ETH/USDT ⚡️⚡️
Exchanges: Binance Futures
Signal Type: Regular (Short)
Leverage: Cross (25.0X)

Entry Targets:
1) 2265 - 100.0% ✅

Take-Profit Targets:
1) 2201 - 33.4% ✅
2) 2181 - 22.2%
3) 2040 - 22.2%
4) 1788 - 22.2%

Stop Targets:
1) 2400

Published By:""", None)

    def test_4(self):
        self._assert_signal(AS, """Pair: FTMUSDT SHORT
Leverage: Cross 50x
Entry: 0.19279
Targets: 0.18874 - 0.18546 - 0.1818 - null
SL: 0.2032""", Signal("FTM", [0.19279], [0.18874, 0.18546, 0.1818], 0.2032, 50))

    def test_5(self):
        coin = None
        try:
            self._assert_signal(AS, """close FTMUSDT""", None)
        except CloseTradeException as exp:
            coin = exp.coin
        self.assertEqual(coin, "FTM")


class TestBAW(TestSignal):
    def test_1(self):
        self._assert_signal(
            BAW, """Long ETH/USDT

Entry 2475 / 2425

Targets 2526 / 2571 / 2613 / 2675 / 2731

Stop loss : 2290

Leverage cross x8

Exchange : Binance Futures

by @CRR""", Signal("ETH", [2475, 2425], [2526, 2571, 2613, 2675, 2731], 2290))


class TestSPP(TestSignal):
    def test_1(self):
        self._assert_signal(SPP, """Lit/Usdt short scalp

Entry : 3.481/3.245

Target : 3.11/3.05/2.98/2.85/2.79/2.66/2.53

Stop 3.63

Lev 4x

Cross

by @CRR""", Signal("LIT", [3.481, 3.245], [3.11, 3.05, 2.98, 2.85, 2.79, 2.66, 2.53], 3.63))

    def test_2(self):
        self.assertRaises(
            CloseTradeException,
            self._assert_signal,
            SPP, "close", None
        )

    def test_3(self):
        self._assert_signal(SPP, """Short BTC/USDT (scalp)

Entry : 42500/41000

Target : 40400/39700/39300/38500/38000

Stop 42800

Lev 10x

by @CRR""", Signal("BTC", [41000, 42500], [40400, 39700, 39300, 38500, 38000], 42800))


class TestKVIP(TestSignal):
    def test_1(self):
        self._assert_signal(KVIP, """📣 Binance Futures Call

  💹SHORT

📌 #ETHUSDT

💰 Entry: 2144-2190

🏹 Tp: 2100-2060-2000-1950-1850

🧨 Stop : 2250

⚖️ Leverage: 3x-5X
✅ Capital %: 3

by @CRR""", Signal("ETH", [2144, 2190], [2100, 2060, 2000, 1950, 1850], 2250))


class TestKK(TestSignal):
    def test_1(self):
        self._assert_signal(KK, """$SAND

 long

 0.646

TP 0.67 0.71$  0.76

Sl 0.62

by @CRR""", Signal("SAND", [0.646], [0.67, 0.71, 0.76], 0.62))

    def test_2(self):
        self._assert_signal(KK, """https://www.tradingview.com/x/3k9ARB7S/


$TLM/USDT entry Update

0.25 0.23

TP 0.41 0.47 0.68

SL 0.2

by @CRR""", Signal("TLM", [0.25, 0.23], [0.41, 0.47, 0.68], 0.2))

    def test_3(self):
        self._assert_signal(KK, """https://www.tradingview.com/

$GRT/USDT

Buy 0.58 0.52

TP 0.64 0.74

SL 0.46

by @CRR""", Signal("GRT", [0.58, 0.52], [0.64, 0.74], 0.46))


class TestBVIP2(TestSignal):
    def test_1(self):
        self._assert_signal(BVIP2, """🔱  #ETH/USDT  🔱

Enter Short 📉

✅ Entry Zone:
2300 - 2340

Take-Profit Targets:

🎯 2380
🎯 2420
🎯 2480
🎯 2599

Leverage × 16

Stop Loss :

🔴  2220""", Signal("ETH", [2300, 2340], [2380, 2420, 2480, 2599], 2220, 16))

    def test_2(self):
        self._assert_signal(
            BVIP2, """https://www.tradingview.com/

Enter Long 📈

MATIC/USDT 1.149

Leverage x7

Targets :

🎯 1.255
🎯 1.349

Stop loss 🔴 1.076

Note :

Was on my watchlist for more than a week and I wanted to see the EMA200 hold.
EMA50/34 pushing well and we're on a good demand zone.""",
            Signal("MATIC", [1.149], [1.255, 1.349], 1.076, 7))


# class TestWC(TestSignal):
#     def test_1(self):
#         self._assert_signal(WC, """Long #IOTA 0.8600$ - 0.8550$ X5 - X10

# Target -0.8750$ -0.8950$ -0.9200$ - 0.9450$ -0.970$

# Stop- 0.780$""", Signal("IOTA", [0.86, 0.855], [0.875, 0.895]))

#     def test_2(self):
#         self._assert_signal(WC, """#Long #BTC - 37380$ - 37300$- X20

# Target-  37600$ - 37780$ - 37920 - 38050$ - 38200$ - 38400$

# Stop- 36800$""", Signal("BTC", [37380, 37300], [37600, 37780, 37920, 38050, 38200, 38400], 36800))
