import asyncio
import logging
from Agents.Orchestrator import RestaurantOrchestrator
from MCP.McpClient import cleanup_mcp_client

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

async def main():
    orchestrator = RestaurantOrchestrator()
    
    try:
        orchestrator.setup_agents()
        
        # Esto cambiarlo una vez que lo integremos con Copilot 
        orders = [
            {"id": "ORD-001", "description": "Preparar una hamburguesa con queso cheddar y tocino"},
            {"id": "ORD-002", "description": "Preparar una pizza familiar con pepperoni y extra queso"},
            {"id": "ORD-003", "description": "Preparar un hot dog con todas las salsas y cebolla caramelizada"},
            {"id": "ORD-004", "description": "Preparar dos hamburguesas dobles con queso y pepinillos"},
            {"id": "ORD-005", "description": "Preparar una pizza vegetariana con champiñones y aceitunas"}
        ]
        
        await orchestrator.process_orders_with_llm_routing(orders)
        
        orchestrator.show_agent_discovery()
        
        logging.info("\n" + "=" * 70)
        logging.info("SISTEMA FINALIZADO CORRECTAMENTE")
        logging.info("=" * 70)
        logging.info("")
        
    finally:
        logging.info("\nCerrando conexiones MCP...")
        await cleanup_mcp_client()
        logging.info("✓ Conexiones cerradas")


if __name__ == "__main__":
    logging.info("\nIniciando Sistema Multi-Agente A2A con MCP Integration...\n")
    
    try:
        import nest_asyncio
        nest_asyncio.apply()
    except ImportError:
        pass
    
    asyncio.run(main())