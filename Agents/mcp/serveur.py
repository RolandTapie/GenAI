from mcp.server.fastmcp import FastMCP

server = FastMCP(
    name="serveur_mcp_test",
    command="python",
    args=['serveur.py'])

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