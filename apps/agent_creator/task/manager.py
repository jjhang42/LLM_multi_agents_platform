import logging
from typing import AsyncIterable
from agent_creator.agent.core import ImageGenerationAgent
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
    """Agent Task Manager for image generation agent."""

    def __init__(self, agent: ImageGenerationAgent):
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
        params: TaskSendParams = request.params
        query = self._get_user_query(params)

        try:
            image_id = self.agent.invoke(query, params.sessionId)
            if not image_id:
                raise ValueError("Agent did not return an image ID.")
            image_data = self.agent.get_image_data(params.sessionId, image_id)
        except Exception as e:
            logger.exception("❌ Error invoking image generation agent")
            error_artifact = Artifact(parts=[{"type": "text", "text": f"Agent error: {e}"}])
            task = await self._update_store(params.id, TaskStatus(state=TaskState.FAILED), [error_artifact])
            return SendTaskResponse(id=request.id, result=task)

        if image_data and not image_data.error:
            file_bytes = (
                image_data.bytes.encode() if isinstance(image_data.bytes, str)
                else image_data.bytes
            )
            file_part = FilePart(
                file=FileContent(
                    bytes=file_bytes,
                    mimeType=image_data.mime_type or "image/png",
                    name=image_data.name or "generated_image.png",
                )
            )
            parts = [file_part]
        else:
            error_msg = image_data.error or "Image generation failed without message."
            logger.warning(f"⚠️ Image generation failed: {error_msg}")
            parts = [{"type": "text", "text": error_msg}]

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
