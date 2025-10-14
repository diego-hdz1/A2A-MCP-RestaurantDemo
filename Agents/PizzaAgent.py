from python_a2a import agent, skill, A2AServer, TaskStatus, TaskState, AgentCard, AgentSkill
from typing import List
import asyncio
from datetime import datetime
import random
import logging

class PizzaAgent(A2AServer):
    """Agente especializado en preparar pizzas"""
    
    def __init__(self, url: str):
        preparar_skill = AgentSkill(
            id="pizza-preparar",
            name="Preparar Pizza",
            description="Prepara una pizza artesanal al horno de piedra con ingredientes frescos",
            tags=["pizza", "horno", "masa", "italiano", "artesanal", "napolitana"],
            examples=[
                "Preparar una pizza margherita",
                "Pizza con pepperoni",
                "Quiero una pizza vegetariana grande"
            ],
        )
        
        agent_card = AgentCard(
            name="Pizza Artisan",
            description="Agente especializado en preparación de pizzas artesanales al horno de piedra estilo napolitano",
            url=url,
            version="1.0.0",
            skills=[preparar_skill],
            default_input_modes=["text"],
            default_output_modes=["text"]
        )
        
        super().__init__(agent_card=agent_card)
        
        logging.info(f"{agent_card.name} inicializado")
        logging.info(f"   └─ URL: {agent_card.url}")
        logging.info(f"   └─ Skills: {len(agent_card.skills)}")
        for skill in agent_card.skills:
            logging.info(f"      • {skill.name}: {skill.description}")


    async def preparar_pizza(self, size: str = "mediana", toppings: List[str] = None):
        """Prepara una pizza paso a paso"""
        if toppings is None:
            toppings = ["pepperoni", "champiñones", "pimientos", "aceitunas"]
        
        logging.info(f"\n[Pizza Artisan] Comenzando preparación de pizza {size}...")
        
        steps = [
            ("Amasando la masa artesanal", 1.5),
            ("Esparciendo salsa de tomate San Marzano", 0.7),
            ("Agregando mozzarella di bufala", 0.8),
            ("Distribuyendo ingredientes premium", 1.0),
            ("Horneando en horno de piedra a 450°C", 2.0),
            ("Cortando en porciones perfectas", 0.5),
            ("Presentación en caja artesanal", 0.5)
        ]
        
        preparation_log = []
        for step, duration in steps:
            logging.info(f"  └─ {step}")
            await asyncio.sleep(duration)
            preparation_log.append({
                "step": step,
                "timestamp": datetime.now().isoformat()
            })
        
        logging.info(f"[Pizza Artisan] ¡Pizza lista y crujiente!")
        
        return {
            "item": "pizza",
            "quality": random.choice(["magistral", "excelente", "premium"]),
            "preparation_time": sum(d for _, d in steps),
            "steps": preparation_log,
            "size": size,
            "toppings": toppings,
            "temperature": "Servida a 85°C"
        }
    
    def handle_task(self, task):
        """Maneja tareas asignadas por el orquestador"""
        message_data = task.message or {}
        content = message_data.get("content", {})
        text = content.get("text", "") if isinstance(content, dict) else str(content)
        
        logging.info(f"\n[Pizza Artisan]  Tarea recibida: {text}")
        
        toppings_default = ["pepperoni premium", "champiñones frescos", "albahaca", "extra queso"]
        
        
        import nest_asyncio
        nest_asyncio.apply()
        loop = asyncio.get_event_loop()
        resultado = loop.run_until_complete(
            self.preparar_pizza("mediana", toppings_default)
        )
        
        task.artifacts = [{
            "parts": [{
                "type": "text",
                "text": f"Pizza preparada al estilo napolitano!\n\n"
                       f"Detalles:\n"
                       f"  • Calidad: {resultado['quality']}\n"
                       f"  • Tiempo: {resultado['preparation_time']:.1f}s\n"
                       f"  • Tamaño: {resultado['size']}\n"
                       f"  • Ingredientes: {', '.join(resultado['toppings'])}\n"
                       f"  • Temperatura: {resultado['temperature']}"
            }]
        }]
        task.status = TaskStatus(state=TaskState.COMPLETED)
        
        return task
