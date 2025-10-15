from python_a2a import agent, skill, A2AServer, TaskStatus, TaskState, AgentCard, AgentSkill
from typing import List
import asyncio
from datetime import datetime
import random
import logging
from MCP.McpClient import get_mcp_client

class HotDogAgent(A2AServer):
    """Agente especializado en preparar hot dogs"""
    
    def __init__(self, url: str):

        preparar_skill = AgentSkill(
            id="hotdog-preparar",
            name="Preparar Hot Dog",
            description="Prepara un hot dog artesanal con toppings personalizados",
            tags=["hot dog", "salchicha", "comida rápida", "artesanal"],
            examples=[
                "Preparar un hot dog con mostaza",
                "Hot dog con todas las salsas",
                "Quiero un hot dog estilo Nueva York"
            ],
        )
        
        agent_card = AgentCard(
            name="Hot Dog Master",
            description="Agente especializado en preparación de hot dogs artesanales estilo Nueva York",
            url=url,
            version="1.0.0",
            skills=[preparar_skill],
            default_input_modes=["text"],
            default_output_modes=["text"]
            # Capabilities ?? 
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

    async def preparar_hotdog(self, toppings: List[str] = None):
        """Prepara un hot dog paso a paso"""
        if toppings is None:
            toppings = ["mostaza", "ketchup", "cebolla", "relish"]
        
        await self._ensure_mcp_connection()

        logging.info(f"\n[Hot Dog Master] Comenzando preparación...")
        
        # 1. Log de inicio usando MCP
        await self.mcp_client.call_tool(
            "log_preparation_start",
            {
                "item_name": "Hamburguesa Gourmet",
                "agent_name": "Hamburguesa Chef"
            }
        )
        
        # TODO: Checar que si sea lo de los toppings y no que sea directamente "ingredientes"
        # 2. Validar ingredientes usando MCP
        await self.mcp_client.call_tool(
            "validate_ingredients",
            {"ingredients": toppings}
        )

        steps = [
            ("Seleccionando salchicha premium", 0.8),
            ("Asando a la perfección", 1.2),
            ("Calentando pan especial", 0.6),
            ("Agregando cebolla caramelizada", 0.5),
            ("Añadiendo salsas gourmet", 0.4),
            ("Presentación final", 0.4)
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

        logging.info(f"[Hot Dog Master] ¡Hot dog listo para disfrutar!")
        
        return {
            "item": "hot_dog",
            "quality": random.choice(["excepcional", "muy buena", "excelente"]),
            "preparation_time": sum(d for _, d in steps),
            "steps": preparation_log,
            "toppings": toppings,
            "style": "Estilo Nueva York"
        }
    
    def handle_task(self, task):
        """Maneja tareas asignadas por el orquestador"""
        message_data = task.message or {}
        content = message_data.get("content", {})
        text = content.get("text", "") if isinstance(content, dict) else str(content)
        
        logging.info(f"\n[Hot Dog Master]  Tarea recibida: {text}")
        
        toppings_default = ["mostaza dijon", "ketchup orgánico", "cebolla crujiente", "jalapeños"]
        
        import nest_asyncio
        nest_asyncio.apply()
        loop = asyncio.get_event_loop()
        resultado = loop.run_until_complete(
            self.preparar_hotdog(toppings_default)
        )
        
        task.artifacts = [{
            "parts": [{
                "type": "text",
                "text": f"Hot Dog preparado con maestría!\n\n"
                       f"Detalles:\n"
                       f"  • Calidad: {resultado['quality']}\n"
                       f"  • Tiempo: {resultado['preparation_time']:.1f}s\n"
                       f"  • Toppings: {', '.join(resultado['toppings'])}\n"
                       f"  • Estilo: {resultado['style']}"
            }]
        }]
        task.status = TaskStatus(state=TaskState.COMPLETED)
        
        return task
    