# agent_publisher/task/manager.py

import logging
from typing import AsyncIterable

from agent_publisher.agent.core import MarkdownPublisherAgent
from core.server_components.task_manager import InMemoryTaskManager
from core.server_components.utils import are_modalities_compatible, new_incompatible_types_error
from core.system.formats.a2a import (
    Artifact,
    FileContent,
    FilePart,
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
    """Task Manager for markdown publishing agent."""

    def __init__(self, agent: MarkdownPublisherAgent):
        super().__init__()
        self.agent = agent

    async def _stream_generator(
        self, request: SendTaskRequest
    ) -> AsyncIterable[SendTaskResponse]:
        raise NotImplementedError("Streaming not supported.")

    async def on_send_task(
        self, request: SendTaskRequest
    ) -> SendTaskResponse | AsyncIterable[SendTaskResponse]:
        if not are_modalities_compatible(
            request.params.acceptedOutputModes,
            self.agent.SUPPORTED_CONTENT_TYPES,
        ):
            logger.warning(
                "❌ Unsupported output mode. Received: %s, Supported: %s",
                request.params.acceptedOutputModes,
                self.agent.SUPPORTED_CONTENT_TYPES,
            )
            return new_incompatible_types_error(request.id)

        await self.upsert_task(request.params)
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
            task = self.tasks.get(task_id)
            if not task:
                logger.error("❌ Task %s not found for update", task_id)
                raise ValueError(f"Task {task_id} not found")

            task.status = status
            if status.message:
                self.task_messages[task_id].append(status.message)
            if artifacts:
                if task.artifacts is None:
                    task.artifacts = []
                task.artifacts.extend(artifacts)
            return task

    async def _invoke(self, request: SendTaskRequest) -> SendTaskResponse:
        params = request.params
        query = self._get_user_query(params)

        try:
            file_path = self.agent.invoke(query, params.sessionId)
            if not file_path:
                raise ValueError("Agent failed to generate markdown.")

            file_data = self.agent.get_file_data(params.sessionId, file_path)
        except Exception as e:
            logger.exception("❌ Error invoking publishing agent")
            error_artifact = Artifact(parts=[{"type": "text", "text": f"Publishing error: {e}"}])
            task = await self._update_store(params.id, TaskStatus(state=TaskState.FAILED), [error_artifact])
            return SendTaskResponse(id=request.id, result=task)

        if file_data and not file_data.error:
            file_part = FilePart(
                file=FileContent(
                    bytes=file_data.bytes.encode() if isinstance(file_data.bytes, str) else file_data.bytes,
                    mimeType=file_data.mime_type or "text/markdown",
                    name=file_data.name or "published_output.md",
                )
            )
            parts = [file_part]
        else:
            error_msg = file_data.error or "Markdown publishing failed."
            parts = [{"type": "text", "text": error_msg}]
            logger.warning(f"⚠️ {error_msg}")

        artifact = Artifact(parts=parts)
        task = await self._update_store(
            params.id,
            TaskStatus(state=TaskState.COMPLETED),
            [artifact],
        )
        return SendTaskResponse(id=request.id, result=task)

    def _get_user_query(self, params: TaskSendParams) -> str:
        part = params.message.parts[0]
        if not isinstance(part, TextPart):
            raise ValueError("Only text parts are supported in this agent.")
        return part.text
