# apps/agent_model/task_manager.py

import logging
from typing import AsyncIterable
from agent import AgentModel
from common.server.task_manager import InMemoryTaskManager
from common.server import utils
from common.types import (
    Artifact,
    JSONRPCResponse,
    SendTaskRequest,
    SendTaskResponse,
    SendTaskStreamingRequest,
    SendTaskStreamingResponse,
    Task,
    TaskSendParams,
    TaskState,
    TaskStatus,
    TextPart,
)

logger = logging.getLogger(__name__)


class AgentTaskManager(InMemoryTaskManager):
    """Agent Task Manager for agent_model."""

    def __init__(self, agent: AgentModel):
        super().__init__()
        self.agent = agent

    async def _stream_generator(
        self, request: SendTaskRequest
    ) -> AsyncIterable[SendTaskResponse]:
        raise NotImplementedError("Streaming not supported.")

    async def on_send_task(
        self, request: SendTaskRequest
    ) -> SendTaskResponse | AsyncIterable[SendTaskResponse]:
        # 입력/출력 모드 호환성 검사
        if not utils.are_modalities_compatible(
            request.params.acceptedOutputModes,
            self.agent.SUPPORTED_CONTENT_TYPES,
        ):
            logger.warning(
                "Unsupported output mode. Received %s, Supported %s",
                request.params.acceptedOutputModes,
                self.agent.SUPPORTED_CONTENT_TYPES,
            )
            return utils.new_incompatible_types_error(request.id)

        task_send_params: TaskSendParams = request.params
        await self.upsert_task(task_send_params)

        return await self._invoke(request)

    async def on_send_task_subscribe(
        self, request: SendTaskStreamingRequest
    ) -> AsyncIterable[SendTaskStreamingResponse] | JSONRPCResponse:
        error = self._validate_request(request)
        if error:
            return error
        await self.upsert_task(request.params)

    async def _update_store(
        self, task_id: str, status: TaskStatus, artifacts: list[Artifact]
    ) -> Task:
        async with self.lock:
            try:
                task = self.tasks[task_id]
            except KeyError as exc:
                logger.error("Task %s not found for update", task_id)
                raise ValueError(f"Task {task_id} not found") from exc

            task.status = status

            if status.message:
                self.task_messages[task_id].append(status.message)

            if artifacts:
                if not task.artifacts:
                    task.artifacts = []
                task.artifacts.extend(artifacts)

            return task

    async def _invoke(self, request: SendTaskRequest) -> SendTaskResponse:
        params = request.params
        query = self._get_user_query(params)

        try:
            result_text = self.agent.invoke(query, params.sessionId)
        except Exception as e:
            logger.error("Error invoking agent: %s", e)
            raise ValueError(f"Agent error: {e}") from e

        artifact = Artifact(parts=[{"type": "text", "text": result_text}])
        task = await self._update_store(
            params.id,
            TaskStatus(state=TaskState.COMPLETED),
            [artifact]
        )
        return SendTaskResponse(id=request.id, result=task)

    def _get_user_query(self, params: TaskSendParams) -> str:
        part = params.message.parts[0]
        if not isinstance(part, TextPart):
            raise ValueError("Only text parts are supported")
        return part.text
