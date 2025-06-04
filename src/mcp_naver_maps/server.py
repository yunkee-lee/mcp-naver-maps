from mcp.server.fastmcp import FastMCP
from mcp_naver_maps.naver_maps_client import NaverMapsClient
from mcp_naver_maps.models import GeocodeResponse, LocalSearchResponse, LocalItem
from dotenv import load_dotenv
from pydantic import Field
from typing import Dict, Literal, List
import math
import logging
import os
import json
from datetime import datetime

load_dotenv()

# 로깅 설정
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../logs')
os.makedirs(log_dir, exist_ok=True)

logger = logging.getLogger('mcp_naver_maps')
logger.setLevel(logging.INFO)

# 파일 핸들러 설정
log_file = os.path.join(log_dir, f'coordinate_search_{datetime.now().strftime("%Y%m%d")}.log')
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)

# 포맷 설정
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# 로거에 핸들러 추가
logger.addHandler(file_handler)

naver_maps_client = NaverMapsClient()

INSTRUCTIONS = """
Naver Maps MCP provides the following <tools>. You must follow all <rules>.

<tools>
- geocode: Searches for address information related to the entered address.
- localSearch: Searches for places related to the given query. Results include addresses.
- localSearchByCoordinate: Searches for places within a specific radius from a coordinate.
</tools>

<rules>
- If the response contains [meta], which is the metadata of a result, you can get paging information from the response.
  If a user wants to get more results, you can call the same tool with an increased [page], if supported, as long as the current page has results.
- When making consecutive calls to the same MCP tool, wait for a random duration between 0 ms and 50ms, and apply exponential backoff between calls.
- For location-based searches, use localSearchByCoordinate when you need to limit results to a specific area.
</rules>
""".strip()

mcp = FastMCP("mcp_naver_maps", instructions=INSTRUCTIONS)


@mcp.tool(description="Searches for address information related to the entered address.")
async def geocode(
  address: str = Field(description="address to search for", min_length=1),
  language: Literal["kor", "eng"] = Field("kor", description="language used in response"),
) -> GeocodeResponse | Dict:
  """
  Returns:
    GeocodeResponse: An object containing metadata and a list of matching addresses
  """
  try:
    return await naver_maps_client.geocode(address, language)
  except Exception as ex:
    return {"success": False, "error": str(ex)}


@mcp.tool(description="Searches for places registered with Naver's local service.")
async def localSearch(
  query: str = Field(description="query used for search", min_length=1),
  display: int = Field(
    5, description="number of search results to display in response", ge=0, le=5
  ),
  sort: Literal["random", "comment"] = Field(
    "random",
    description="sorting method. random: sorted by correctness. comment: sorted by a number of reviews (descending)",
  ),
) -> LocalSearchResponse | Dict:
  """
  Returns:
    LocalSearchResponse: An object containing places registered with Naver's local service.
  """
  try:
    return await naver_maps_client.searchForLocalInformation(query, display, sort)
  except Exception as ex:
    return {"success": False, "error": str(ex)}


@mcp.tool(description="Searches for places within a specific radius from a coordinate.")
async def localSearchByCoordinate(
  query: str = Field(description="query used for search, should have regional information (like OOO 근처) for better search", min_length=1),
  longitude: float = Field(description="center longitude (x coordinate)"),
  latitude: float = Field(description="center latitude (y coordinate)"),
  radius: int = Field(1000, description="search radius in meters (default: 1000m = 1km)", ge=1, le=10000),
  display: int = Field(
    5, description="number of search results to display in response", ge=0, le=5
  ),
  sort: Literal["random", "comment"] = Field(
    "random",
    description="sorting method. random: sorted by correctness. comment: sorted by a number of reviews (descending)",
  ),
  min_results: int = Field(1, description="minimum number of results to return", ge=1, le=5),
) -> LocalSearchResponse | Dict:
  """
  Returns:
    LocalSearchResponse: An object containing places registered with Naver's local service within the specified radius.
  """
  try:
    # 입력 파라미터 로깅
    input_params = {
      "query": query,
      "longitude": longitude,
      "latitude": latitude,
      "radius": radius,
      "display": display,
      "sort": sort,
      "min_results": min_results
    }
    logger.info(f"localSearchByCoordinate - Input: {json.dumps(input_params, ensure_ascii=False)}")
    
    filtered_items = []
    start = 1
    max_attempts = 20  # 최대 20페이지까지만 검색
    search_stats = {"pages_searched": 0, "total_items_found": 0, "filtered_items": 0}
    
    while len(filtered_items) < min_results and start <= max_attempts:
      # 검색 수행
      response = await naver_maps_client.searchForLocalInformation(query, display, sort, start)
      search_stats["pages_searched"] += 1
      
      # 중간 조회 결과 로깅
      logger.info(f"localSearchByCoordinate - Page {start} results: total={response.total}, items={len(response.items)}")
      if response.items:

        logger.info(f"localSearchByCoordinate - Page {start} items: {json.dumps(response.items, ensure_ascii=False)}")
      
      if not response.items:
        break
      
      search_stats["total_items_found"] += len(response.items)
      
      # 좌표 기반 필터링
      for item in response.items:
        if hasattr(item, 'mapx') and hasattr(item, 'mapy'):
          item_lon = float(item.mapx) / 10_000_000
          item_lat = float(item.mapy) / 10_000_000
          
          # 거리 계산 (Haversine 공식)
          distance = calculate_distance(longitude, latitude, item_lon, item_lat)
          
          # 반경 내에 있는 항목만 추가
          if distance <= radius:
            filtered_items.append(item)
            search_stats["filtered_items"] += 1
      
      # 다음 페이지로
      start += 1
      
      # 충분한 결과를 찾았거나 더 이상 결과가 없으면 종료
      if len(filtered_items) >= min_results or response.total <= (start-1) * display:
        break
    
    # 결과 구성
    result = LocalSearchResponse(
      total=len(filtered_items),
      start=1,
      display=len(filtered_items),
      items=filtered_items[:display]
    )
    
    # 출력 결과 로깅
    output_summary = {
      "total_results": len(filtered_items),
      "displayed_results": min(len(filtered_items), display),
      "search_stats": search_stats
    }
    logger.info(f"localSearchByCoordinate - Output: {json.dumps(output_summary, ensure_ascii=False)}")
    
    # 검색된 항목 로깅
    if filtered_items:
      item_titles = [item.title for item in filtered_items[:display]]
      logger.info(f"localSearchByCoordinate - Found items: {json.dumps(item_titles, ensure_ascii=False)}")
    
    return result
  except Exception as ex:
    error_msg = str(ex)
    logger.error(f"localSearchByCoordinate - Error: {error_msg}")
    return {"success": False, "error": error_msg}


def calculate_distance(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
  """
  두 지점 간의 거리를 미터 단위로 계산 (Haversine 공식)
  """
  R = 6371000  # 지구 반경 (미터)
  
  # 라디안으로 변환
  lat1_rad = math.radians(lat1)
  lon1_rad = math.radians(lon1)
  lat2_rad = math.radians(lat2)
  lon2_rad = math.radians(lon2)
  
  # 위도와 경도의 차이
  dlat = lat2_rad - lat1_rad
  dlon = lon2_rad - lon1_rad
  
  # Haversine 공식
  a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
  c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
  distance = R * c
  
  return distance
