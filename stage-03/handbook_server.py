from mcp.server import MCPServer
from chunk_compare import TEXT, smart_chunks, build, search

mcp = MCPServer("Handbook")

@mcp.tool()
def search_handbook(query: str) -> str:
    """Search the tool library handbook. Read only."""
    db = build(smart_chunks(TEXT))  # small, so rebuilt per call
    return "\n---\n".join(search(db, query, 3))

@mcp.tool()
def add_note(text: str) -> str:
    """Add a note to the handbook. This one writes."""
    return "note added"  # a stand-in: it changes nothing here

if __name__ == "__main__":
    mcp.run()  # talks over stdin and stdout
