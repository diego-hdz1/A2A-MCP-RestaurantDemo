from typing import Any
import logging
import asyncio
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("restaurant-tools")

@mcp.tool()
async def log_preparation_start(item_name: str, agent_name: str) -> str:
    """Log cuando un agente comienza la preparación de un item.
    
    Args:
        item_name: Nombre del item a preparar
        agent_name: Nombre del agente que prepara
    """
    message = f"[MCP LOG] {agent_name} ha iniciado la preparación de: {item_name}"
    logging.info(message)
    await asyncio.sleep(0.1)
    return message

@mcp.tool()
async def log_preparation_complete(item_name: str, agent_name: str, preparation_time: float) -> str:
    """Log cuando un agente completa la preparación de un item.
    
    Args:
        item_name: Nombre del item preparado
        agent_name: Nombre del agente que preparó
        preparation_time: Tiempo de preparación en segundos
    """
    message = f"[MCP LOG] {agent_name} completó {item_name} en {preparation_time:.1f}s"
    logging.info(message)
    await asyncio.sleep(0.1)
    return message

@mcp.tool()
async def validate_ingredients(ingredients: list[str]) -> str:
    """Valida que los ingredientes estén disponibles en inventario.
    
    Args:
        ingredients: Lista de ingredientes a validar
    """
    # Simulación de validación de inventario
    available = ["carne", "queso", "lechuga", "tomate", "pan", "tocino", "salsa", "cebolla", "pepinillos"]
    
    missing = [ing for ing in ingredients if ing.lower() not in available]
    
    if missing:
        message = f"[MCP LOG] Ingredientes faltantes: {', '.join(missing)}"
    else:
        message = f"[MCP LOG] Todos los ingredientes disponibles: {', '.join(ingredients)}"
    
    logging.info(message)
    await asyncio.sleep(0.1)
    return message

@mcp.tool()
async def get_quality_score(item_type: str, preparation_time: float) -> str:
    """Calcula un score de calidad basado en el tiempo de preparación.
    
    Args:
        item_type: Tipo de item (hamburguesa, pizza, hotdog)
        preparation_time: Tiempo que tomó preparar
    """

    ideal_times = {
        "hamburguesa": 5.0,
        "pizza": 8.0,
        "hotdog": 3.0
    }
    
    ideal = ideal_times.get(item_type.lower(), 5.0)
    difference = abs(preparation_time - ideal)
    
    if difference < 1.0:
        quality = "Premium"
        score = 95
    elif difference < 2.0:
        quality = "Excelente"
        score = 85
    elif difference < 3.0:
        quality = "Muy Buena"
        score = 75
    else:
        quality = "Buena"
        score = 65
    
    message = f"[MCP LOG] Score de calidad para {item_type}: {quality} ({score}/100)"
    logging.info(message)
    await asyncio.sleep(0.1)
    return message

def main():
    """Initialize and run the MCP server"""
    logging.info("Iniciando servidor MCP para Restaurant Tools...")
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()