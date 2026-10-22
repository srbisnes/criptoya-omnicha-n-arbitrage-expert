# CryptoYa Omnichaín Arbitrage Expert

**El experto en arbitrajes que se alimenta en tiempo real de la API pública de CriptoYa.**

Detecta oportunidades de arbitraje CEX ↔ CEX / P2P en Latinoamérica (ARS, BRL, CLP, COP, MXN, etc.), calcula **ganancia neta** descontando fees de retiro, y sugiere caminos omnichaín (Layer 0-1-2-3).

## Características

- Escaneo multi-coin (USDT, USDC, BTC, ETH, DAI…)
- Multi-fiat LATAM
- Comparación ask/bid + totalAsk/totalBid
- Incorporación de fees de retiro (`/api/fees`)
- Ranking por % de ganancia neta
- Dashboard web liviano (HTML + JS)
- Listo para alertas, bots o integración con IA
- Arquitectura preparada para LayerZero / Axelar / CCIP / Wormhole

## API Base

```
https://criptoya.com/api
```

- Cotización agregada: `/api/{coin}/{fiat}/{volumen}`
- Cotización por exchange: `/api/{exchange}/{coin}/{fiat}/{volumen}`
- Fees: `/api/fees`
- Dólar: `/api/dolar`

Límite: 120 req/min. Sin autenticación.

## Uso rápido

```bash
pip install requests
python arbitrage_scanner.py
```

O abrí `index.html` en el navegador (el dashboard corre 100% client-side).

## Arquitectura Omnichaín

1. **Detección** (CryptoYa) → compra barata / venta cara
2. **Settlement** → sugerencia de red óptima (BSC, Arbitrum, Polygon, Solana, Tron, etc.)
3. **Bridge Layer** → posible path LayerZero / Axelar / CCTP para mover el activo
4. **Profit neto** → después de fees + gas estimado

## Deploy

- GitHub: este repo
- Vercel: importá el repo (el `index.html` sirve como static)

---

**Elcryptoboy Architecture** — Web1 + Web2 + Web3 + Fintech + Tokens + Smart Contracts + Layers 0-1-2-3
