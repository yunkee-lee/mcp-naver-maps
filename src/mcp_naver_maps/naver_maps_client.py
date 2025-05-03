import httpx
import os

from enum import StrEnum
from typing import Any

class DirectionOption(StrEnum):
  FAST = "trfast",
  COMFORT = "tracomfort",
  OPTIMAL = "traoptimal",
  AVOID_TOLL = "travoidtoll",
  AVOID_CARD_ONLY = "traavoidcaronly"

class NaverMapsClient:

  BASE_URL = "https://maps.apigw.ntruss.com"

  def __init__(self):
    self.client_id = os.getenv("NAVER_MAPS_CLIENT_ID")
    self.client_secret = os.getenv("NAVER_MAPS_CLIENT_SECRET")
    if not self.client_id or not self.client_secret:
      raise AuthError("Missing client id or client secret")
    
    self.headers = {
      "x-ncp-apigw-api-key-id": self.client_id,
      "x-ncp-apigw-api-key": self.client_secret,
      "Accept": "application/json"
    }

  async def geocode(
    self,
    query: str,
    language: str,
    page: int = 1,
    count: int = 10,
  ) -> list:
    path = f"{self.BASE_URL}/map-geocode/v2/geocode"
    params = {
      "query": query,
      "language": language,
      "page": page,
      "count": count,
    }
    return (await self._get(path, params)).get("addresses", [])
  
  async def directions(
    self,
    start: str,
    goal: str,
    language:  str,
    direction_option: DirectionOption,
  ):
    path = f"{self.BASE_URL}/map-direction/v1/driving"
    params = {
      "start": start,
      "goal": goal,
      "option": str(direction_option),
      "lang": language,
    }
    return (await self._get(path, params)).get("route", {})

  async def _get(self, path: str, params: dict[str, Any]) -> Any:
    async with httpx.AsyncClient(headers=self.headers, http2=True) as client:
      response = await client.get(path, params=params)

      try:
        return response.raise_for_status().json()
      except httpx.HTTPError as exc:
        self._handle_response_status(response.status_code, exc)
    
  def _handle_response_status(self, http_status_code: int, http_error: httpx.HTTPError):
    error_str = str(http_error)
    if http_status_code == 400:
      raise BadRequestError(error_str)
    if http_status_code == 401:
      raise AuthError(error_str)
    if http_status_code == 420:
      raise RateLimitError(error_str)
    if http_status_code != 200:
      raise NaverMapsClientError(f"Unexpected error [status_code={http_status_code}, error={error_str}]")

class NaverMapsClientError(Exception):
  def __init__(self, message: str):
    self.message = message
    super().__init__(self.message)

class BadRequestError(NaverMapsClientError):
  def __init__(self, message):
    super().__init__(f"Bad request: {message}")

class AuthError(NaverMapsClientError):
  def __init__(self, message):
    super().__init__(f"Auth error: {message}")

class RateLimitError(NaverMapsClientError):
  def __init__(self, message):
    super().__init__(f"Rate limited: {message}")
