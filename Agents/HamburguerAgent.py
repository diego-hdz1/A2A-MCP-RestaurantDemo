from python_a2a import agent, skill, A2AServer, TaskStatus, TaskState, AgentCard, AgentSkill
from typing import List
import asyncio
from datetime import datetime
import random
import logging
from MCP.McpClient import get_mcp_client

class HamburguesaAgent(A2AServer):
    """Agente especializado en preparar hamburguesas con integración MCP"""
    
    def __init__(self, url: str):

        preparar_skill = AgentSkill(
            id="hamburguesa-preparar",
            name="Preparar Hamburguesa",
            description="Prepara una hamburguesa gourmet con ingredientes especificados",
            tags=["hamburguesa", "carne", "parrilla", "comida rápida", "gourmet"],
            examples=[
                "Preparar una hamburguesa con queso",
                "Quiero una hamburguesa doble con tocino",
                "Hamburguesa vegetariana"
            ],
        )
        
        agent_card = AgentCard(
            name="Hamburguesa Chef",
            description="Agente especializado en preparación de hamburguesas gourmet con ingredientes premium",
            url=url,
            version="1.0.0",
            skills=[preparar_skill],
            default_input_modes=["text"],
            default_output_modes=["text"]
        )
        
        super().__init__(agent_card=agent_card)
        
        self.mcp_client = None
        
        logging.info(f"{agent_card.name} inicializado")
        logging.info(f"   └─ URL: {agent_card.url}")
        logging.info(f"   └─ Skills: {len(agent_card.skills)}")
        for skill in agent_card.skills:
            logging.info(f"      • {skill.name}: {skill.description}")

    async def _ensure_mcp_connection(self):
        """Asegura que hay una conexión MCP activa"""
        if self.mcp_client is None:
            self.mcp_client = await get_mcp_client()
            # Listar tools disponibles
            await self.mcp_client.list_tools()

    async def preparar_hamburguesa(self, ingredientes: List[str] = None):
        """Prepara una hamburguesa paso a paso con llamadas MCP"""
        if ingredientes is None:
            ingredientes = ["carne", "pan", "lechuga", "tomate", "queso"]
        
        await self._ensure_mcp_connection()
        
        logging.info(f"\n[Hamburguesa Chef] Comenzando preparación...")
        
        # 1. Log de inicio usando MCP
        await self.mcp_client.call_tool(
            "log_preparation_start",
            {
                "item_name": "Hamburguesa Gourmet",
                "agent_name": "Hamburguesa Chef"
            }
        )
        
        # 2. Validar ingredientes usando MCP
        await self.mcp_client.call_tool(
            "validate_ingredients",
            {"ingredients": ingredientes}
        )
        
        # 3. Proceso de preparación
        steps = [
            ("Preparando la carne de res premium", 1.0),
            ("Cocinando a la parrilla a punto medio", 1.5),
            ("Tostando el pan brioche", 0.8),
            ("Añadiendo vegetales frescos", 0.7),
            ("Agregando queso cheddar artesanal", 0.5),
            ("Empaquetando con cuidado", 0.5)
        ]
        
        preparation_log = []
        for step, duration in steps:
            logging.info(f"  └─ {step}")
            await asyncio.sleep(duration)
            preparation_log.append({
                "step": step,
                "timestamp": datetime.now().isoformat()
            })
        
        total_time = sum(d for _, d in steps)
        
        # 4. Log de completado usando MCP
        await self.mcp_client.call_tool(
            "log_preparation_complete",
            {
                "item_name": "Hamburguesa Gourmet",
                "agent_name": "Hamburguesa Chef",
                "preparation_time": total_time
            }
        )
        
        # 5. Obtener score de calidad usando MCP
        quality_result = await self.mcp_client.call_tool(
            "get_quality_score",
            {
                "item_type": "hamburguesa",
                "preparation_time": total_time
            }
        )
        
        logging.info(f"[Hamburguesa Chef] ¡Hamburguesa lista para servir!")
        logging.info(f"[Hamburguesa Chef] {quality_result}")
        
        return {
            "item": "hamburguesa",
            "quality": random.choice(["excelente", "muy buena", "premium"]),
            "preparation_time": total_time,
            "steps": preparation_log,
            "ingredients": ingredientes,
            "temperature": "Caliente (75°C)",
            "mcp_quality_check": quality_result
        }
    
    def handle_task(self, task):
        """Maneja tareas asignadas por el orquestador"""
        message_data = task.message or {}
        content = message_data.get("content", {})
        text = content.get("text", "") if isinstance(content, dict) else str(content)
        
        logging.info(f"\n[Hamburguesa Chef] Tarea recibida: {text}")
        
        ingredientes_default = ["carne", "queso", "lechuga", "tomate", "salsa especial"]
        
        import nest_asyncio
        nest_asyncio.apply()
        loop = asyncio.get_event_loop()
        resultado = loop.run_until_complete(
            self.preparar_hamburguesa(ingredientes_default)
        )
        
        task.artifacts = [{
            "parts": [{
                "type": "text",
                "text": f"Hamburguesa preparada exitosamente!\n\n"
                       f"Detalles:\n"
                       f"  • Calidad: {resultado['quality']}\n"
                       f"  • Tiempo: {resultado['preparation_time']:.1f}s\n"
                       f"  • Ingredientes: {', '.join(resultado['ingredients'])}\n"
                       f"  • Temperatura: {resultado['temperature']}\n"
                       f"  • MCP Quality Check: Completado ✓"
            }]
        }]
        task.status = TaskStatus(state=TaskState.COMPLETED)
        
        return task