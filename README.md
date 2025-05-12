# MCP Naver Maps

The MCP connects to the [Naver Maps API](https://www.ncloud.com/product/applicationService/maps) and [Naver Search API](https://developers.naver.com/products/service-api/search/search.md)

It currently supports the following APIs:
* [Geocoding](https://api.ncloud-docs.com/docs/application-maps-geocoding)
* [Local saerch](https://developers.naver.com/docs/serviceapi/search/local/local.md#%EC%A7%80%EC%97%AD)

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
    NAVER_CLIENT_SECRET="YOUR_NAVER_CLIENT_SECRET
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
