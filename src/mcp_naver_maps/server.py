from mcp.server.fastmcp import FastMCP
from mcp_naver_maps.naver_maps_client import NaverMapsClient
from mcp_naver_maps.models import GeocodeResponse, LocalSearchResponse
from dotenv import load_dotenv
from pydantic import Field
from typing import Dict, Literal

load_dotenv()

naver_maps_client = NaverMapsClient()

INSTRUCTIONS = """
Naver Maps MCP provides the following <tools>. You must follow all <rules>.

<tools>
- geocode: Searches for address information related to the entered address.
- localSearch: Searches for places related to the given query. Results include addresses.
</tools>

<rules>
- If the response contains [meta], which is the metadata of a result, you can get paging information from the response.
  If a user wants to get more results, you can call the same tool with an increased [page], if supported, as long as the current page has results.
- When making consecutive calls to the same MCP tool, wait for a random duration between 0 ms and 50ms, and apply exponential backoff between calls.
</rules>
""".strip()

mcp = FastMCP("mcp_naver_maps", instructions=INSTRUCTIONS)

@mcp.tool(description="Searches for address information related to the entered address.")
async def geocode(
  address: str = Field(description="address to search for", min_length=1),
  language: Literal["kor", "eng"] = Field("kor", description="language used in response")
) -> GeocodeResponse | Dict:
  """
  Returns:
    GeocodeResponse: An object containing metadata and a list of matching addresses
  """
  try:
    return await naver_maps_client.geocode(address, language)
  except Exception as ex:
    return { "success": False, "error": str(ex) }

@mcp.tool(description="Searches for places registered with Naver's local service.")
async def localSearch(
  query: str = Field(description="query used for search", min_length=1),
  display: int = Field(5, description="number of search results to display in response", ge=0, le=5),
  sort: Literal["random", "comment"] = Field("random", description="sorting method. random: sorted by correctness. comment: sorted by a number of reviews (descending)"),
) -> LocalSearchResponse | Dict:
  """
  Returns:
    LocalSearchResponse: An object containing places registered with Naver's local service.
  """
  try:
    return await naver_maps_client.searchForLocalInformation(query, display, sort)
  except Exception as ex:
    return { "success": False, "error": str(ex) }
