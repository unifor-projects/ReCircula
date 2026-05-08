"""Geocodificação de CEP brasileiro.

Fluxo:
1. Chama a API ViaCEP para obter dados de endereço (logradouro, localidade, uf).
2. Usa o OpenStreetMap Nominatim para converter o endereço em coordenadas (lat, lon).

Retorna ``None`` em qualquer campo em caso de falha (ex.: CEP inválido, serviço
indisponível), para que a criação do anúncio não seja bloqueada.
"""

from __future__ import annotations

import logging
import math
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

_VIACEP_URL = "https://viacep.com.br/ws/{cep}/json/"
_NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
_NOMINATIM_HEADERS = {"User-Agent": "ReCircula/1.0 (recircula@gmail.com)"}
_HTTP_TIMEOUT = 5.0  # seconds


async def geocode_cep(cep: str) -> tuple[Optional[float], Optional[float]]:
    """Retorna ``(latitude, longitude)`` para o *cep* fornecido.

    Args:
        cep: CEP brasileiro, com ou sem hífen (ex.: ``"60180-160"`` ou ``"60180160"``).

    Returns:
        Tupla ``(lat, lon)`` em graus decimais, ou ``(None, None)`` se não for
        possível geocodificar.
    """
    cep_digits = cep.replace("-", "").strip()
    if len(cep_digits) != 8 or not cep_digits.isdigit():
        return None, None

    address_query = await _viacep_to_query(cep_digits)
    if not address_query:
        return None, None

    # Tentar variações da consulta no Nominatim, removendo primeiro o bairro,
    # depois rua+bairro, e por fim a cidade (deixando apenas UF e país).
    parts = [p.strip() for p in address_query.split(",") if p.strip()]

    def join_nonempty(items: list[str]) -> str:
        return ", ".join(p for p in items if p)

    variants: list[str] = []
    # 1) consulta completa
    variants.append(join_nonempty(parts))

    # 2) remover bairro (assumindo formato: logradouro, bairro, localidade, uf, Brazil)
    if len(parts) >= 3:
        v = [parts[0]] + parts[2:]
        variants.append(join_nonempty(v))

    # 3) remover rua e bairro -> apenas localidade, uf, Brazil
    if len(parts) >= 3:
        v = parts[2:]
        variants.append(join_nonempty(v))

    # 4) remover cidade -> manter apenas UF e país (últimos dois elementos)
    if len(parts) >= 2:
        v = parts[-2:]
        variants.append(join_nonempty(v))

    # Remover duplicatas preservando ordem
    seen = set()
    unique_variants: list[str] = []
    for q in variants:
        if q and q not in seen:
            seen.add(q)
            unique_variants.append(q)

    for q in unique_variants:
        logger.debug("Nominatim: tentando consulta variante: %s", q)
        lat, lon = await _nominatim_geocode(q)
        if lat is not None and lon is not None:
            return lat, lon

    # Se nenhuma variante funcionou, retorna None
    return None, None


async def _viacep_to_query(cep_digits: str) -> Optional[str]:
    """Chama ViaCEP e monta uma string de endereço para geocodificação."""
    url = _VIACEP_URL.format(cep=cep_digits)
    try:
        async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT) as client:
            resp = await client.get(url)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:  # network errors, timeouts, bad JSON…
        logger.warning("ViaCEP error for CEP %s: %s", cep_digits, exc)
        return None

    if data.get("erro"):
        logger.info("ViaCEP: CEP %s not found", cep_digits)
        return None

    parts = [
        data.get("logradouro") or "",
        data.get("bairro") or "",
        data.get("localidade") or "",
        data.get("uf") or "",
        "Brazil",
    ]
    return ", ".join(p for p in parts if p)

async def _nominatim_geocode(query: str) -> tuple[Optional[float], Optional[float]]:
    """Geocodifica *query* via Nominatim e retorna ``(lat, lon)``."""
    params = {"q": query, "format": "json", "limit": 1, "countrycodes": "br"}
    try:
        async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT) as client:
            resp = await client.get(
                _NOMINATIM_URL, params=params, headers=_NOMINATIM_HEADERS
            )
        resp.raise_for_status()
        results = resp.json()
    except Exception as exc:
        logger.warning("Nominatim error for query '%s': %s", query, exc)
        return None, None

    if not results:
        logger.info("Nominatim: no results for '%s'", query)
        return None, None

    try:
        lat = float(results[0]["lat"])
        lon = float(results[0]["lon"])
        return lat, lon
    except (KeyError, ValueError, TypeError) as exc:
        logger.warning("Nominatim: unexpected result format: %s", exc)
        return None, None


# ---------------------------------------------------------------------------
# Pure-Python Haversine helper (used for in-memory sorting / filtering)
# ---------------------------------------------------------------------------

_EARTH_RADIUS_KM = 6371.0


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Retorna a distância em km entre dois pontos geográficos (Haversine)."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * _EARTH_RADIUS_KM * math.asin(math.sqrt(a))
