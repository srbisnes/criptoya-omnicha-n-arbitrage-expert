#!/usr/bin/env python3
"""
CryptoYa Omnichaín Arbitrage Expert
Se alimenta exclusivamente de la API pública de CriptoYa.
Detecta oportunidades de compra baja / venta alta con profit neto.
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional

BASE = "https://criptoya.com/api"

COINS = ["USDT", "USDC", "BTC", "ETH", "DAI"]
FIATS = ["ARS", "BRL", "CLP", "COP", "MXN", "PEN", "UYU"]
VOLUMES = {"USDT": 1000, "USDC": 1000, "BTC": 0.01, "ETH": 0.1, "DAI": 1000}

MIN_PROFIT_PCT = 0.3  # mínimo % para mostrar

def fetch_quotes(coin: str, fiat: str, volume: float) -> Optional[Dict]:
    url = f"{BASE}/{coin}/{fiat}/{volume}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200 and r.text != "Invalid pair":
            return r.json()
    except Exception as e:
        print(f"Error fetching {coin}/{fiat}: {e}")
    return None

def fetch_fees() -> Dict:
    try:
        r = requests.get(f"{BASE}/fees", timeout=15)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return {}

def estimate_withdraw_fee(fees: Dict, exchange: str, coin: str) -> float:
    """Estimación simple del fee de retiro (toma el mínimo de las redes disponibles)."""
    if exchange not in fees or coin not in fees[exchange]:
        return 0.0
    networks = fees[exchange][coin]
    min_fee = float("inf")
    for net, data in networks.items():
        if isinstance(data, dict) and "withdraw" in data:
            fee = data["withdraw"]
            if fee < min_fee:
                min_fee = fee
    return min_fee if min_fee != float("inf") else 0.0

def find_arbitrage(quotes: Dict, fees: Dict, coin: str, fiat: str, volume: float) -> List[Dict]:
    opportunities = []
    exchanges = list(quotes.keys())
    
    for buy_ex in exchanges:
        buy_data = quotes[buy_ex]
        buy_price = buy_data.get("totalAsk") or buy_data.get("ask")
        if not buy_price or buy_price <= 0:
            continue
            
        for sell_ex in exchanges:
            if buy_ex == sell_ex:
                continue
            sell_data = quotes[sell_ex]
            sell_price = sell_data.get("totalBid") or sell_data.get("bid")
            if not sell_price or sell_price <= 0:
                continue
            
            raw_profit_pct = ((sell_price - buy_price) / buy_price) * 100
            if raw_profit_pct < MIN_PROFIT_PCT:
                continue
            
            # Fee de retiro estimado (en unidades del coin)
            withdraw_fee = estimate_withdraw_fee(fees, buy_ex, coin)
            fee_impact_pct = (withdraw_fee / volume) * 100 if volume else 0
            
            net_profit_pct = raw_profit_pct - fee_impact_pct - 0.15  # 0.15% buffer gas/slippage
            
            if net_profit_pct > 0:
                opportunities.append({
                    "coin": coin,
                    "fiat": fiat,
                    "volume": volume,
                    "buy_exchange": buy_ex,
                    "sell_exchange": sell_ex,
                    "buy_price": round(buy_price, 4),
                    "sell_price": round(sell_price, 4),
                    "raw_profit_pct": round(raw_profit_pct, 3),
                    "withdraw_fee": withdraw_fee,
                    "net_profit_pct": round(net_profit_pct, 3),
                    "estimated_profit_fiat": round((sell_price - buy_price) * volume - (withdraw_fee * buy_price), 2),
                    "timestamp": datetime.utcnow().isoformat()
                })
    
    return sorted(opportunities, key=lambda x: x["net_profit_pct"], reverse=True)

def main():
    print("=== CryptoYa Omnichaín Arbitrage Expert ===")
    print(f"Escaneando a las {datetime.now().strftime('%H:%M:%S')}...\n")
    
    fees = fetch_fees()
    all_ops = []
    
    for coin in COINS:
        volume = VOLUMES.get(coin, 100)
        for fiat in FIATS:
            quotes = fetch_quotes(coin, fiat, volume)
            if not quotes:
                continue
            ops = find_arbitrage(quotes, fees, coin, fiat, volume)
            all_ops.extend(ops[:5])  # top 5 por par
            if ops:
                print(f"[{coin}/{fiat}] {len(ops)} oportunidades detectadas")
    
    all_ops = sorted(all_ops, key=lambda x: x["net_profit_pct"], reverse=True)[:30]
    
    print("\n" + "="*80)
    print("TOP OPORTUNIDADES (Net Profit)")
    print("="*80)
    
    for i, op in enumerate(all_ops[:15], 1):
        print(f"{i:2}. {op['coin']}/{op['fiat']} | Buy {op['buy_exchange']} @ {op['buy_price']} → Sell {op['sell_exchange']} @ {op['sell_price']}")
        print(f"    Raw: {op['raw_profit_pct']}% | Net: {op['net_profit_pct']}% | Est. profit: {op['estimated_profit_fiat']} {op['fiat']}")
        print(f"    Withdraw fee ~{op['withdraw_fee']} {op['coin']}\n")
    
    # Guardar JSON para el dashboard o bots
    with open("opportunities.json", "w") as f:
        json.dump(all_ops, f, indent=2)
    
    print(f"\nTotal oportunidades guardadas en opportunities.json: {len(all_ops)}")
    print("Listo para integrar con alertas, IA o smart contracts omnichaín.")

if __name__ == "__main__":
    main()
