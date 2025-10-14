from python_a2a import AgentNetwork
import asyncio
import logging
from typing import List, Dict
from Agents.HamburguerAgent import HamburguesaAgent
from Agents.PizzaAgent import PizzaAgent
from Agents.HotDogAgent import HotDogAgent

class RestaurantOrchestrator:
    """Orquestador que coordina los agentes usando AgentCards y Skills"""
    
    def __init__(self):
        self.network = AgentNetwork(name="Restaurant Agent Network")
        self.agents = {}  
        self.completed_orders = []
        
    def setup_agents(self):
        """Configura y registra todos los agentes"""
        logging.info("=" * 70)
        logging.info("INICIANDO SISTEMA MULTI-AGENTE A2A - RESTAURANTE VIRTUAL")
        logging.info("=" * 70)
        logging.info("")
        logging.info("Configurando agentes especializados con AgentCard y AgentSkill...\n")
        
        hamburguesa_agent = HamburguesaAgent(url="http://localhost:5001")
        hotdog_agent = HotDogAgent(url="http://localhost:5002")
        pizza_agent = PizzaAgent(url="http://localhost:5003")
        
        # Guardar referencias con acceso a AgentCard
        self.agents = {
            "hamburguesa": hamburguesa_agent,
            "hotdog": hotdog_agent,
            "pizza": pizza_agent
        }
        
        # Registrar en la red
        for name, agent in self.agents.items():
            self.network.add(name, agent.agent_card.url)
        
        logging.info("")
        return hamburguesa_agent, hotdog_agent, pizza_agent
    

    # Esto se va a cambiar por integracion con LLM 
    async def process_orders_with_llm_routing(self, orders: List[Dict]):
        """Procesa pedidos con enrutamiento inteligente basado en AgentCards"""
        logging.info("\n" + "=" * 70)
        logging.info("PROCESAMIENTO DE PEDIDOS CON ROUTING INTELIGENTE")
        logging.info("=" * 70)
        logging.info("")
        
        for i, order in enumerate(orders, 1):
            logging.info(f"\n{'─' * 70}")
            logging.info(f"PEDIDO #{i}: {order['description']}")
            logging.info(f"{'─' * 70}")
            
            # Simular análisis LLM usando AgentCards y Skills
            logging.info(f"\nAnalizando capacidades de agentes...")
            selected_agent_name = self._smart_route(order['description'])
            
            logging.info(f"Agente seleccionado: {selected_agent_name.upper()}")
            
            agent = self.agents[selected_agent_name]
            agent_card = agent.agent_card
            
            logging.info(f"Agent Card: {agent_card.name}")
            logging.info(f"   └─ Skills disponibles: {len(agent_card.skills)}")
            for skill in agent_card.skills:
                logging.info(f"      • {skill.name} ({', '.join(skill.tags)})")
            
            # Crear y procesar tarea
            class SimpleTask:
                def __init__(self):
                    self.message = None
                    self.status = None
                    self.artifacts = []
            
            task = SimpleTask()
            task.message = {"content": {"text": order['description']}}
            
            # Procesar tarea
            result_task = agent.handle_task(task)
            
            # Guardar resultado
            self.completed_orders.append({
                "order_id": i,
                "description": order['description'],
                "agent": selected_agent_name,
                "agent_card": agent_card.name,
                "skills_used": [skill.name for skill in agent_card.skills],
                "status": "completed",
                "result": result_task.artifacts[0]["parts"][0]["text"] if result_task.artifacts else "N/A"
            })
            
            await asyncio.sleep(0.5)
        
        self._print_summary()
    

    # Esto se va a cambiar por integracion con LLM 
    def _smart_route(self, description: str) -> str:
        """
        Enrutamiento inteligente basado en AgentCards y Skills
        Simula un LLM analizando las capacidades de cada agente
        """
        desc_lower = description.lower()
        
        scores = {}
        for name, agent in self.agents.items():
            score = 0
            agent_card = agent.agent_card
            
            for skill in agent_card.skills:
                for tag in skill.tags:
                    if tag.lower() in desc_lower:
                        score += 10
                
                for example in skill.examples:
                    if any(word in desc_lower for word in example.lower().split()):
                        score += 5
            
            desc_words = agent_card.description.lower().split()
            for word in desc_words:
                if word in desc_lower:
                    score += 2
            
            scores[name] = score
            logging.info(f"   └─ {agent_card.name}: score = {score}")
        
        best_agent = max(scores, key=scores.get)
        return best_agent
    
    def _print_summary(self):
        """Imprime resumen detallado con información de AgentCards"""
        logging.info("\n\n" + "=" * 70)
        logging.info("RESUMEN DE OPERACIONES - RESTAURANTE VIRTUAL")
        logging.info("=" * 70)
        logging.info("")
        
        for order in self.completed_orders:
            logging.info(f"PEDIDO #{order['order_id']}")
            logging.info(f"   Descripción: {order['description']}")
            logging.info(f"   Agente: {order['agent_card']}")
            logging.info(f"   Skills usadas: {', '.join(order['skills_used'])}")
            logging.info(f"   Estado: {order['status'].upper()}")
            logging.info("")
            for line in order['result'].split('\n'):
                if line.strip():
                    logging.info(f"   {line}")
            logging.info("")
    
    def show_agent_discovery(self):
        """Muestra el proceso de descubrimiento de agentes"""
        logging.info("\n" + "=" * 70)
        logging.info("DESCUBRIMIENTO DE AGENTES - AGENT CARDS DISPONIBLES")
        logging.info("=" * 70)
        logging.info("")
        
        for name, agent in self.agents.items():
            card = agent.agent_card
            logging.info(f"{card.name}")
            logging.info(f"   ID: {name}")
            logging.info(f"   Descripción: {card.description}")
            logging.info(f"   URL: {card.url}")
            logging.info(f"   Versión: {card.version}")
            logging.info(f"   Skills ({len(card.skills)}):")
            logging.info(f"      └─ Input: {card.default_input_modes}")
            logging.info(f"      └─ Output: {card.default_output_modes}")
            
            for skill in card.skills:
                logging.info(f"      • {skill.name}")
                logging.info(f"        ├─ ID: {skill.id}")
                logging.info(f"        ├─ Descripción: {skill.description}")
                logging.info(f"        ├─ Tags: {', '.join(skill.tags)}")
                logging.info(f"        └─ Ejemplos: {len(skill.examples)}")
                for example in skill.examples[:2]:  # Mostrar solo 2 ejemplos
                    logging.info(f"           · {example}")
            logging.info("")