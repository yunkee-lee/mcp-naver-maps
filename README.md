# MCP Naver Maps

The MCP connects to the [Naver Maps API](https://www.ncloud.com/product/applicationService/maps) and [Naver Search API](https://developers.naver.com/products/service-api/search/search.md). 네이버 지도 API와 검색 API에 (로컬) 연결하는 MCP 서버.

It currently supports the following APIs:
* [Geocoding](https://api.ncloud-docs.com/docs/application-maps-geocoding)
* [Local search](https://developers.naver.com/docs/serviceapi/search/local/local.md#%EC%A7%80%EC%97%AD)
* [Coordinate-based local search](#coordinate-based-local-search) - Search for places within a specific radius from coordinates

## Prerequisites

Before you begin, ensure you have the following installed:

* **Python:** Version 3.13 or higher
* **uv:** You can find installation instructions [here](https://github.com/astral-sh/uv).
* **Naver Cloud Platform Account:** You need API credentials (Client ID and Client Secret) for the Naver Maps service. You can obtain these from the [Naver Cloud Platform console](https://www.ncloud.com/).
* **Naver Develoeprs Account:** You need API credentials (Client ID and Client Secret) for the Naver Developers API. You can obtain these from the [Naver Developers](https://developers.naver.com/main/).

## Configuration

1. **Create a `.env` file:**  Create a file in the project root.

2. **Add API Credentials:** Edit the `.env` file and add your Naver Maps API credentials and Naver Developers API credentials.
    ```.env
    NAVER_MAPS_CLIENT_ID="YOUR_NAVER_MAPS_CLIENT_ID"
    NAVER_MAPS_CLIENT_SECRET="YOUR_NAVER_MAPS_CLIENT_SECRET"
    NAVER_CLIENT_API="YOUR_NAVER_CLIENT_API"
    NAVER_CLIENT_SECRET="YOUR_NAVER_CLIENT_SECRET"
    ```
    Please verify the exact environment variable names required by checking `src/mcp_naver_maps/naver_maps_client.py`.

## Running the MCP

1. **Sync Dependencies:** Navigate to the project root directory in your terminal and run the following command. This will create a virtual environment (if one doesn't exist) and install all dependencies specified in `pyproject.toml`.
    ```bash
    uv sync
    ```

2. **Run:**: You can run the MCP server using `uv`.
    ```bash
    uv run src/mcp_naver_maps
    ```

    For development,
    ```bash
    source .venv/bin/activate
    mcp dev src/mcp_naver_maps/server.py
    ```

## MCP Configuration

To configure this MCP in your environment, add the following to your MCP configuration:

```json
"mcpServers": {
    "mcp-naver-location": {
        "command": "uv",
        "args": ["run", "/path/to/mcp-naver-maps/src/mcp_naver_maps"],
        "env": {
            "NAVER_MAPS_CLIENT_ID": "<YOUR_NAVER_MAPS_CLIENT_ID>",
            "NAVER_MAPS_CLIENT_SECRET": "<YOUR_NAVER_MAPS_CLIENT_SECRET>",
            "NAVER_CLIENT_API": "<YOUR_NAVER_CLIENT_API>",
            "NAVER_CLIENT_SECRET": "<YOUR_NAVER_CLIENT_SECRET>"
        }
    }
}
```

Replace the placeholder values with your actual Naver API credentials.

## Coordinate-based Local Search

This feature allows you to search for places within a specific radius from given coordinates.

### Usage

```python
result = await localSearchByCoordinate(
    query="카페",                # Search query
    longitude=126.9707,         # Center longitude (x coordinate)
    latitude=37.5536,           # Center latitude (y coordinate)
    radius=1000,                # Search radius in meters (default: 1000m = 1km)
    display=5,                  # Maximum number of results to display (default: 5)
    sort="random",              # Sorting method (default: "random")
    min_results=1               # Minimum number of results to return (default: 1)
)
```

### Parameters

- **query** (required): Search query string
- **longitude** (required): Center longitude (x coordinate)
- **latitude** (required): Center latitude (y coordinate)
- **radius** (optional): Search radius in meters, default is 1000m (1km)
- **display** (optional): Maximum number of results to display, default is 5
- **sort** (optional): Sorting method, either "random" (by relevance) or "comment" (by number of reviews)
- **min_results** (optional): Minimum number of results to return, default is 1

### Example Prompts

```
서울역(경도: 126.9707, 위도: 37.5536) 주변 1km 이내의 맛집을 찾아줘.
```

```
센터필드 EAST 좌표를 찾아서 반경 700m 이내의 맛집을 추천해줘. 
- 검색할 때는 '역삼동 근처 고기구이'처럼 지역명을 포함해서 검색
- 색인할 음식 주제: [삼겹살, 갈비, LA갈비, 양갈비, 곱창, 닭갈비] 등 육류
```
