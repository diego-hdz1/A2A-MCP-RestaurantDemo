from python_a2a import agent, skill, A2AServer, TaskStatus, TaskState, AgentCard, AgentSkill
from typing import List
import asyncio
from datetime import datetime
import random
import logging

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
        
        logging.info(f"{agent_card.name} inicializado")
        logging.info(f"   └─ URL: {agent_card.url}")
        logging.info(f"   └─ Skills: {len(agent_card.skills)}")
        for skill in agent_card.skills:
            logging.info(f"      • {skill.name}: {skill.description}")


    # Aqui puede ir la llamada a la tool del MCP server
    async def preparar_hotdog(self, toppings: List[str] = None):
        """Prepara un hot dog paso a paso"""
        if toppings is None:
            toppings = ["mostaza", "ketchup", "cebolla", "relish"]
        
        logging.info(f"\n[Hot Dog Master] Comenzando preparación...")
        
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
    