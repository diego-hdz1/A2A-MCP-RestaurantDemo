import asyncio
import logging
from typing import Any
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPClient:
    """Cliente para interactuar con el servidor MCP"""
    
    def __init__(self, server_script_path: str = "MCP/McpServer.py"):
        self.server_script_path = server_script_path
        self.session: ClientSession | None = None
        self.exit_stack = AsyncExitStack()
        self._connected = False
        
    async def connect(self):
        """Establece conexión con el servidor MCP"""
        if self._connected:
            logging.info("[MCP Client] Ya está conectado")
            return True
            
        try:
            server_params = StdioServerParameters(
                command="python",
                args=[self.server_script_path],
                env=None
            )
            
            # Usar AsyncExitStack para manejar correctamente los context managers
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            read_stream, write_stream = stdio_transport
            
            # Crear y entrar en la sesión
            self.session = ClientSession(read_stream, write_stream)
            await self.exit_stack.enter_async_context(self.session)
            
            # Inicializar sesión
            await self.session.initialize()
            
            self._connected = True
            logging.info("[MCP Client] ✓ Conectado al servidor MCP")
            
            # Pequeño delay para asegurar que la conexión está estable
            await asyncio.sleep(0.1)
            
            return True
            
        except Exception as e:
            logging.error(f"[MCP Client] ✗ Error al conectar: {e}")
            await self._cleanup()
            return False
    
    async def _cleanup(self):
        """Limpieza interna de recursos"""
        try:
            await self.exit_stack.aclose()
        except Exception as e:
            logging.debug(f"[MCP Client] Error en cleanup interno: {e}")
        finally:
            self.session = None
            self._connected = False
    
    async def disconnect(self):
        """Cierra la conexión con el servidor MCP"""
        if not self._connected:
            logging.debug("[MCP Client] No hay conexión activa para cerrar")
            return
            
        try:
            logging.info("[MCP Client] Cerrando conexión...")
            await self._cleanup()
            logging.info("[MCP Client] ✓ Desconectado del servidor MCP")
        except Exception as e:
            logging.error(f"[MCP Client] Error al desconectar: {e}")
    
    async def list_tools(self) -> list:
        """Lista todas las herramientas disponibles en el servidor MCP"""
        if not self._connected or not self.session:
            logging.error("[MCP Client] No hay sesión activa")
            return []
        
        try:
            result = await self.session.list_tools()
            tools = result.tools if hasattr(result, 'tools') else []
            logging.info(f"[MCP Client] Tools disponibles: {len(tools)}")
            for tool in tools:
                logging.info(f"   • {tool.name}: {tool.description}")
            return tools
        except Exception as e:
            logging.error(f"[MCP Client] Error al listar tools: {e}")
            return []
    
    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Llama a una herramienta del servidor MCP
        
        Args:
            tool_name: Nombre de la herramienta
            arguments: Argumentos para la herramienta
        """
        if not self._connected or not self.session:
            logging.error("[MCP Client] No hay sesión activa")
            return None
        
        try:
            logging.info(f"[MCP Client] → Llamando a tool: {tool_name}")
            logging.debug(f"[MCP Client]   Argumentos: {arguments}")
            
            result = await self.session.call_tool(tool_name, arguments=arguments)
            
            # Extraer contenido de la respuesta
            if hasattr(result, 'content') and result.content:
                content = result.content[0]
                if hasattr(content, 'text'):
                    logging.info(f"[MCP Client] ← Respuesta recibida")
                    return content.text
            
            return str(result)
            
        except Exception as e:
            logging.error(f"[MCP Client] ✗ Error al llamar tool {tool_name}: {e}")
            return None
    
    def is_connected(self) -> bool:
        """Verifica si hay una conexión activa"""
        return self._connected and self.session is not None


# Cliente global singleton
_mcp_client_instance: MCPClient | None = None
_mcp_client_lock = asyncio.Lock()

async def get_mcp_client(server_path: str = "MCP/McpServer.py") -> MCPClient:
    """Obtiene o crea la instancia singleton del cliente MCP
    
    Args:
        server_path: Ruta al script del servidor MCP
    """
    global _mcp_client_instance
    
    async with _mcp_client_lock:
        if _mcp_client_instance is None:
            logging.info("[MCP Client] Inicializando cliente MCP...")
            _mcp_client_instance = MCPClient(server_path)
            success = await _mcp_client_instance.connect()
            
            if not success:
                _mcp_client_instance = None
                raise RuntimeError("No se pudo conectar al servidor MCP")
        
        return _mcp_client_instance

async def cleanup_mcp_client():
    """Cierra el cliente MCP global"""
    global _mcp_client_instance
    
    async with _mcp_client_lock:
        if _mcp_client_instance:
            await _mcp_client_instance.disconnect()
            _mcp_client_instance = None
            logging.debug("[MCP Client] Cliente global limpiado")