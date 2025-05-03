from mcp.server.fastmcp import FastMCP
from mcp_naver_maps.naver_maps_client import DirectionOption, NaverMapsClient
from dotenv import load_dotenv

load_dotenv()

naver_maps_client = NaverMapsClient()

INSTRUCTIONS = """
Naver Maps MCP provides tools for searching for address information and getting directions within South Korea.

- geocode: Searches for address information related to the entered address.
""".strip()

mcp = FastMCP("mcp_naver_maps", instructions=INSTRUCTIONS)

@mcp.tool()
async def geocode(address: str, language: str = "kor") -> list:
  """Searches for address information related to the entered address.

  Args:
    address (str): Address to search
    language (str): Language used in response ("kor" or "eng")

  Returns:
    a list of addresses
     - roadAddress (str): address based on a street addresss
     - jibunAddress (str): address based on a lot number
     - englishAddress (str): address in English
     - addressElements (list): details about the found address
     - x (str): x coordiate, longitude
     - y (str): y coordiate, latitude
  """
  try:
    return await naver_maps_client.geocode(address, language)
  except Exception as ex:
    return { "success": False, "error": str(ex) }
  
@mcp.tool()
async def direction(
  start: tuple[str, str],
  destination: tuple[str, str],
  language: str = "ko",
  direction_option: DirectionOption = DirectionOption.OPTIMAL,
) -> dict:
  """Retrieves route and traffic information based on the start and destination

  Args:
    start (tuple[str, str]): longitude and latitude of the start
    destination (tuple[str, str]): longitude and latitude of the destimation
    language (str): Language used in response ("ko", "en", "ja", or "zh")
    direction_option (DirectionOption): Route search option

  Returns:
    route and traffic information
    - see 
  """
  assert len(start) == 2
  assert len(destination) == 2

  try:
    return await naver_maps_client.directions(",".join(start), (",").join(destination), language, direction_option)
  except Exception as ex:
    return { "success": False, "error": str(ex) }
