import asyncio, sys
from mcp import Client
from mcp.client.stdio import StdioServerParameters

SERVER = StdioServerParameters(command=sys.executable,
                               args=["handbook_server.py"])
ALLOWED = {"search_handbook"}  # the only tool we will call

async def main():
    async with Client(SERVER) as client:
        listing = await client.list_tools()
        for tool in listing.tools:
            ok = "allowed" if tool.name in ALLOWED else "no"
            print(f"{ok}: {tool.name} - {tool.description}")
        result = await client.call_tool(
            "search_handbook", {"query": "late fee maximum"})
        print(result.content[0].text[:200])

asyncio.run(main())
