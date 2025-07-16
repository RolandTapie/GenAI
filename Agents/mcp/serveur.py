from mcp.server.fastmcp import FastMCP

server = FastMCP(
    name="serveur_mcp_test",
    host="0.0.0.0",  # only used for SSE transport (localhost)
    port=8050,  # only used for SSE transport (set this to any port)
    stateless_http=True)

@server.tool()
def print_test(data: str):
    """
    il s'agit d'un tool test
    :param data:
    :return:
    """
    return ("Merci " + data)



if __name__ == "__main__":
   server.run(transport="stdio")