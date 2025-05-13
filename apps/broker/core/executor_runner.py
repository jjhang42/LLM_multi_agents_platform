# broker/executor_runner.py

import httpx
import asyncio
from core.system.formats.a2a import Task
from core.system.formats.agent_card import AgentCard
from apps.broker.core.agent_card_loader import AgentCardLoader
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ExecutorRunner:
    def __init__(self, card_loader: AgentCardLoader):
        self.card_loader = card_loader

    async def send_task_to_agent(self, task: Task, agent_card: AgentCard) -> Dict[str, Any]:
        try:
            url = f"{agent_card.url}/run"
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=task.dict())
                response.raise_for_status()
                return {
                    "task_id": task.id,
                    "result": response.json(),
                    "status": "success",
                    "agent": agent_card.name
                }
        except Exception as e:
            logger.error(f"❌ Task {task.id} 실행 실패 on {agent_card.name}: {e}")
            return {
                "task_id": task.id,
                "result": str(e),
                "status": "error",
                "agent": agent_card.name
            }

    async def run_task(self, task: Task) -> Dict[str, Any]:
        try:
            agent_name = task.metadata.get("agent")
            action = task.metadata.get("action")
    
            if agent_name:
                logger.info(f"🔁 Task {task.id}: 명시된 agent → '{agent_name}'")
                card = self.card_loader.get_card_by_name(agent_name)
    
            elif action and action != "unknown":
                logger.info(f"🔁 Task {task.id}: action → '{action}'")
                card = self.card_loader.get_first_card_for_action(action)
    
            else:
                logger.warning(f"⚠ Task {task.id}: action 없음 또는 unknown → researcher fallback")
                card = self.card_loader.get_card_by_name("researcher")
    
            return await self.send_task_to_agent(task, card)
    
        except Exception as e:
            logger.error(f"❌ run_task 실패: {e}")
            return {
                "task_id": task.id,
                "result": str(e),
                "status": "error"
            }

    async def run_tasks(self, tasks: List[Task]) -> List[Dict[str, Any]]:
        return await asyncio.gather(*[self.run_task(task) for task in tasks])
