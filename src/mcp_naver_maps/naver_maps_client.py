import httpx
import os

from mcp_naver_maps.models import GeocodeResponse, LocalSearchResponse
from typing import Dict, Literal


class NaverMapsClient:
  MAP_BASE_URL = "https://maps.apigw.ntruss.com"
  SEARCH_BASE_URL = "https://openapi.naver.com/v1/search"

  def __init__(self):
    naver_client_id = os.getenv("NAVER_CLIENT_API")
    naver_client_secret = os.getenv("NAVER_CLIENT_SECRET")
    if not naver_client_id or not naver_client_secret:
      raise AuthError("Missing client id or client secret for Naver API")

    maps_client_id = os.getenv("NAVER_MAPS_CLIENT_ID")
    maps_client_secret = os.getenv("NAVER_MAPS_CLIENT_SECRET")
    if not maps_client_id or not maps_client_secret:
      raise AuthError("Missing client id or client secret for Naver Maps API")

    self.naver_headers = {
      "X-Naver-Client-Id": naver_client_id,
      "X-Naver-Client-Secret": naver_client_secret,
      "Accept": "application/json",
    }
    self.naver_maps_headers = {
      "x-ncp-apigw-api-key-id": maps_client_id,
      "x-ncp-apigw-api-key": maps_client_secret,
      "Accept": "application/json",
    }

  async def geocode(
    self,
    query: str,
    language: str,
    page: int = 1,
    count: int = 10,
  ) -> GeocodeResponse:
    """
    https://api.ncloud-docs.com/docs/application-maps-geocoding
    """
    path = f"{self.MAP_BASE_URL}/map-geocode/v2/geocode"
    params = {
      "query": query,
      "language": language,
      "page": page,
      "count": count,
    }
    response_json = await self._get(path, self.naver_maps_headers, params)
    return GeocodeResponse(**response_json)

  async def searchForLocalInformation(
    self, query: str, display: int = 5, sort: Literal["random", "comment"] = "random"
  ) -> LocalSearchResponse:
    """
    https://developers.naver.com/docs/serviceapi/search/local/local.md#%EC%A7%80%EC%97%AD
    """
    path = f"{self.SEARCH_BASE_URL}/local.json"
    params = {
      "query": query,
      "display": display,
      "sort": sort,
    }
    response_json = await self._get(path, self.naver_headers, params)
    return LocalSearchResponse(**response_json)

  async def _get(self, path: str, headers: Dict, params: Dict) -> Dict:
    async with httpx.AsyncClient(headers=headers, http2=True) as client:
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
      raise NaverMapsClientError(
        f"Unexpected error [status_code={http_status_code}, error={error_str}]"
      )


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
