#!/usr/bin/env python3
"""
Plantos MCP Server
Exposes agricultural intelligence API as MCP tools for Claude and other AI assistants
"""
import asyncio
import os
from typing import Any
import httpx
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
from pydantic import AnyUrl


# Configure API endpoint
PLANTOS_API_BASE = os.getenv("PLANTOS_API_URL", "http://localhost:8000")
PLANTOS_API_KEY = os.getenv("PLANTOS_API_KEY", "test-key-local-dev")

# Create MCP server instance
server = Server("plantos-agricultural-intelligence")


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """
    List all available Plantos agricultural intelligence tools
    """
    return [
        Tool(
            name="analyze_farm_location",
            description=(
                "Comprehensive agricultural analysis for a specific location. "
                "Provides soil properties, crop yield predictions, weather data, "
                "market intelligence, economic analysis, and AI-generated recommendations. "
                "Returns complete farming intelligence package including optimal crop selection."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "latitude": {
                        "type": "number",
                        "description": "Latitude coordinate of the farm location",
                        "minimum": -90,
                        "maximum": 90
                    },
                    "longitude": {
                        "type": "number",
                        "description": "Longitude coordinate of the farm location",
                        "minimum": -180,
                        "maximum": 180
                    }
                },
                "required": ["latitude", "longitude"]
            }
        ),
        Tool(
            name="get_soil_data",
            description=(
                "Get detailed soil properties for a specific location using SSURGO database. "
                "Returns soil texture, composition, drainage, pH, organic matter, and other properties."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "latitude": {
                        "type": "number",
                        "description": "Latitude coordinate",
                        "minimum": -90,
                        "maximum": 90
                    },
                    "longitude": {
                        "type": "number",
                        "description": "Longitude coordinate",
                        "minimum": -180,
                        "maximum": 180
                    }
                },
                "required": ["latitude", "longitude"]
            }
        ),
        Tool(
            name="get_weather_data",
            description=(
                "Get current weather data from NOAA Weather.gov API for a location. "
                "Includes temperature, precipitation, humidity, growing degree days, and wind data. "
                "This data is used in crop yield prediction models."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "latitude": {
                        "type": "number",
                        "description": "Latitude coordinate",
                        "minimum": -90,
                        "maximum": 90
                    },
                    "longitude": {
                        "type": "number",
                        "description": "Longitude coordinate",
                        "minimum": -180,
                        "maximum": 180
                    }
                },
                "required": ["latitude", "longitude"]
            }
        ),
        Tool(
            name="get_market_data",
            description=(
                "Get live commodity market data for specified crops. "
                "Returns current prices, futures prices, price trends from USDA and CME. "
                "Can include location-based regional price adjustments."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "crops": {
                        "type": "string",
                        "description": "Comma-separated list of crop types (e.g., 'corn,soybeans,wheat')",
                        "default": "corn,soybeans,wheat"
                    },
                    "latitude": {
                        "type": "number",
                        "description": "Optional: Latitude for regional price adjustments",
                        "minimum": -90,
                        "maximum": 90
                    },
                    "longitude": {
                        "type": "number",
                        "description": "Optional: Longitude for regional price adjustments",
                        "minimum": -180,
                        "maximum": 180
                    }
                },
                "required": ["crops"]
            }
        ),
        Tool(
            name="get_market_summary",
            description=(
                "Get comprehensive market summary with location-based insights. "
                "Provides market overview, trends, and regional price context."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "latitude": {
                        "type": "number",
                        "description": "Optional: Latitude for regional context",
                        "minimum": -90,
                        "maximum": 90
                    },
                    "longitude": {
                        "type": "number",
                        "description": "Optional: Longitude for regional context",
                        "minimum": -180,
                        "maximum": 180
                    }
                }
            }
        ),
        Tool(
            name="chat_with_agricultural_advisor",
            description=(
                "Ask questions to an AI agricultural advisor powered by RAG (Retrieval Augmented Generation). "
                "The advisor has access to agricultural research papers, best practices, and farming knowledge. "
                "Provides evidence-based recommendations with source citations. "
                "You can provide optional context from previous interactions."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Your question or message to the agricultural advisor"
                    },
                    "context": {
                        "type": "object",
                        "description": "Optional context including location, soil, weather, crops, and economics data",
                        "properties": {
                            "location": {"type": "object"},
                            "soil_properties": {"type": "object"},
                            "weather_data": {"type": "object"},
                            "crop_predictions": {"type": "array"},
                            "economic_analysis": {"type": "array"}
                        }
                    }
                },
                "required": ["message"]
            }
        ),
        Tool(
            name="get_api_health",
            description=(
                "Check the health status of the Plantos API and database connection. "
                "Useful for troubleshooting or verifying the service is available."
            ),
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[TextContent | ImageContent | EmbeddedResource]:
    """
    Handle tool execution requests from MCP clients
    """
    if arguments is None:
        arguments = {}

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            headers = {
                "X-API-Key": PLANTOS_API_KEY,
                "Content-Type": "application/json"
            }

            if name == "analyze_farm_location":
                response = await client.post(
                    f"{PLANTOS_API_BASE}/api/v1/analyze-location",
                    json={"latitude": arguments["latitude"], "longitude": arguments["longitude"]},
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()

                return [
                    TextContent(
                        type="text",
                        text=f"""# Farm Location Analysis

**Location:** {arguments['latitude']}, {arguments['longitude']}

## Soil Properties
{_format_soil_data(data.get('soil_properties', {}))}

## Weather Conditions
{_format_weather_data(data.get('weather_data', {}))}

## Crop Yield Predictions
{_format_crop_predictions(data.get('crop_predictions', []))}

## Market Data
{_format_market_data(data.get('market_data', []))}

## Economic Analysis
{_format_economic_analysis(data.get('economic_analysis', []))}

## Recommendations
{_format_recommendations(data.get('recommendations', []))}

---
*Analysis generated at {data.get('analysis_timestamp', 'N/A')}*
"""
                    )
                ]

            elif name == "get_soil_data":
                response = await client.get(
                    f"{PLANTOS_API_BASE}/api/v1/soil-data",
                    params={"latitude": arguments["latitude"], "longitude": arguments["longitude"]},
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()

                return [
                    TextContent(
                        type="text",
                        text=f"""# Soil Data for {arguments['latitude']}, {arguments['longitude']}

{_format_soil_data(data)}
"""
                    )
                ]

            elif name == "get_weather_data":
                response = await client.get(
                    f"{PLANTOS_API_BASE}/api/v1/weather-data",
                    params={"latitude": arguments["latitude"], "longitude": arguments["longitude"]},
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()

                return [
                    TextContent(
                        type="text",
                        text=f"""# Weather Data for {arguments['latitude']}, {arguments['longitude']}

**Source:** {data.get('source', 'N/A')}

{_format_weather_data(data.get('weather', {}))}

{data.get('note', '')}
"""
                    )
                ]

            elif name == "get_market_data":
                params = {"crops": arguments["crops"]}
                if "latitude" in arguments:
                    params["latitude"] = arguments["latitude"]
                if "longitude" in arguments:
                    params["longitude"] = arguments["longitude"]

                response = await client.get(
                    f"{PLANTOS_API_BASE}/api/v1/market-data",
                    params=params,
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()

                location_note = ""
                if data.get('location_info', {}).get('regional_adjustments_applied'):
                    location_note = f"\n*Regional price adjustments applied for {data['location_info']['latitude']}, {data['location_info']['longitude']}*"

                return [
                    TextContent(
                        type="text",
                        text=f"""# Market Data

{_format_market_data(data.get('crops', []))}

**Last Updated:** {data.get('last_updated', 'N/A')}
{data.get('note', '')}
{location_note}
"""
                    )
                ]

            elif name == "get_market_summary":
                params = {}
                if "latitude" in arguments:
                    params["latitude"] = arguments["latitude"]
                if "longitude" in arguments:
                    params["longitude"] = arguments["longitude"]

                response = await client.get(
                    f"{PLANTOS_API_BASE}/api/v1/market-summary",
                    params=params,
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()

                return [
                    TextContent(
                        type="text",
                        text=f"""# Market Summary

{_format_dict_recursive(data)}
"""
                    )
                ]

            elif name == "chat_with_agricultural_advisor":
                response = await client.post(
                    f"{PLANTOS_API_BASE}/api/v1/chat",
                    json={
                        "message": arguments["message"],
                        "context": arguments.get("context", {})
                    },
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()

                sources_text = ""
                if data.get('sources'):
                    sources_text = "\n\n## Sources\n" + "\n".join([f"- {source}" for source in data['sources']])

                confidence_text = ""
                if 'confidence' in data:
                    confidence_text = f"\n\n*Confidence: {data['confidence']:.0%}*"

                return [
                    TextContent(
                        type="text",
                        text=f"""{data['response']}{sources_text}{confidence_text}"""
                    )
                ]

            elif name == "get_api_health":
                response = await client.get(
                    f"{PLANTOS_API_BASE}/api/v1/health",
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()

                return [
                    TextContent(
                        type="text",
                        text=f"""# Plantos API Health

**Status:** {data.get('status', 'unknown')}
**Database Connected:** {data.get('database_connected', False)}
**Timestamp:** {data.get('timestamp', 'N/A')}
"""
                    )
                ]

            else:
                return [
                    TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )
                ]

    except httpx.HTTPStatusError as e:
        error_detail = e.response.text
        return [
            TextContent(
                type="text",
                text=f"Error calling Plantos API: {e.response.status_code}\n{error_detail}"
            )
        ]
    except Exception as e:
        return [
            TextContent(
                type="text",
                text=f"Error executing tool: {str(e)}"
            )
        ]


# Helper formatting functions

def _format_soil_data(soil: dict) -> str:
    """Format soil properties as readable text"""
    if not soil:
        return "*No soil data available*"

    lines = []
    if soil.get('soil_texture'):
        lines.append(f"**Texture:** {soil['soil_texture']}")
    if soil.get('drainage_class'):
        lines.append(f"**Drainage:** {soil['drainage_class']}")
    if soil.get('ph_level'):
        lines.append(f"**pH Level:** {soil['ph_level']}")
    if soil.get('organic_matter_pct'):
        lines.append(f"**Organic Matter:** {soil['organic_matter_pct']}%")
    if soil.get('sand_pct') is not None:
        lines.append(f"**Sand:** {soil['sand_pct']}%")
    if soil.get('silt_pct') is not None:
        lines.append(f"**Silt:** {soil['silt_pct']}%")
    if soil.get('clay_pct') is not None:
        lines.append(f"**Clay:** {soil['clay_pct']}%")

    return "\n".join(lines) if lines else "*Soil data incomplete*"


def _format_weather_data(weather: dict) -> str:
    """Format weather data as readable text"""
    if not weather:
        return "*No weather data available*"

    lines = []
    if weather.get('current_temperature'):
        lines.append(f"**Temperature:** {weather['current_temperature']}°F")
    if weather.get('max_temperature'):
        lines.append(f"**Max Temp:** {weather['max_temperature']}°F")
    if weather.get('min_temperature'):
        lines.append(f"**Min Temp:** {weather['min_temperature']}°F")
    if weather.get('avg_relative_humidity'):
        lines.append(f"**Humidity:** {weather['avg_relative_humidity']}%")
    if weather.get('total_precipitation'):
        lines.append(f"**Precipitation:** {weather['total_precipitation']} inches")
    if weather.get('growing_degree_days'):
        lines.append(f"**Growing Degree Days:** {weather['growing_degree_days']}")
    if weather.get('wind_speed_mph'):
        lines.append(f"**Wind Speed:** {weather['wind_speed_mph']} mph")

    return "\n".join(lines) if lines else "*Weather data incomplete*"


def _format_crop_predictions(predictions: list) -> str:
    """Format crop predictions as readable text"""
    if not predictions:
        return "*No predictions available*"

    lines = []
    for pred in predictions:
        crop_name = pred.get('crop_type', 'Unknown').title()
        yield_val = pred.get('predicted_yield', 0)
        confidence = pred.get('confidence_interval', {})

        line = f"**{crop_name}:** {yield_val:.1f} bushels/acre"
        if confidence:
            line += f" (range: {confidence.get('lower', 0):.1f} - {confidence.get('upper', 0):.1f})"
        lines.append(line)

    return "\n".join(lines)


def _format_market_data(market_data: list) -> str:
    """Format market data as readable text"""
    if not market_data:
        return "*No market data available*"

    lines = []
    for item in market_data:
        if isinstance(item, dict):
            crop = item.get('crop_type', 'Unknown').title()
            current = item.get('current_price', 0)
            futures = item.get('futures_price', 0)
            trend = item.get('price_trend', 'unknown')

            lines.append(f"**{crop}:**")
            lines.append(f"  - Current: ${current:.2f}/bu")
            lines.append(f"  - Futures: ${futures:.2f}/bu")
            lines.append(f"  - Trend: {trend}")
            lines.append("")

    return "\n".join(lines)


def _format_economic_analysis(economics: list) -> str:
    """Format economic analysis as readable text"""
    if not economics:
        return "*No economic analysis available*"

    lines = []
    for econ in economics:
        crop = econ.get('crop_type', 'Unknown').title()
        revenue = econ.get('estimated_revenue_per_acre', 0)
        costs = econ.get('estimated_input_costs', 0)
        profit = econ.get('net_profit_per_acre', 0)
        roi = econ.get('roi_percentage', 0)

        lines.append(f"**{crop}:**")
        lines.append(f"  - Revenue: ${revenue:.2f}/acre")
        lines.append(f"  - Costs: ${costs:.2f}/acre")
        lines.append(f"  - Profit: ${profit:.2f}/acre")
        lines.append(f"  - ROI: {roi:.1f}%")
        lines.append("")

    return "\n".join(lines)


def _format_recommendations(recommendations: list) -> str:
    """Format recommendations as readable text"""
    if not recommendations:
        return "*No recommendations available*"

    return "\n".join([f"- {rec}" for rec in recommendations])


def _format_dict_recursive(data: dict, indent: int = 0) -> str:
    """Recursively format nested dictionary data"""
    lines = []
    prefix = "  " * indent

    for key, value in data.items():
        formatted_key = key.replace('_', ' ').title()
        if isinstance(value, dict):
            lines.append(f"{prefix}**{formatted_key}:**")
            lines.append(_format_dict_recursive(value, indent + 1))
        elif isinstance(value, list):
            lines.append(f"{prefix}**{formatted_key}:**")
            for item in value:
                if isinstance(item, dict):
                    lines.append(_format_dict_recursive(item, indent + 1))
                else:
                    lines.append(f"{prefix}  - {item}")
        else:
            lines.append(f"{prefix}**{formatted_key}:** {value}")

    return "\n".join(lines)


async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="plantos-agricultural-intelligence",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
