import logging
from typing import AsyncIterable

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
    def __init__(self, agent):
        super().__init__()
        self.agent = agent

    async def _stream_generator(self, request: SendTaskRequest) -> AsyncIterable[SendTaskResponse]:
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

    async def _invoke(self, request: SendTaskRequest) -> SendTaskResponse:
        params = request.params
        query = self._get_user_query(params)

        try:
            result_id = self.agent.invoke(query, params.sessionId)
            if not result_id:
                raise ValueError("Agent did not return a result.")

            artifact = self._postprocess_result(params.sessionId, result_id)
            status = TaskStatus(state=TaskState.COMPLETED)
        except Exception as e:
            logger.exception("❌ Agent invoke failed")
            artifact = Artifact(parts=[{"type": "text", "text": f"Agent error: {e}"}])
            status = TaskStatus(state=TaskState.FAILED)

        task = await self._update_store(params.id, status, [artifact])
        return SendTaskResponse(id=request.id, result=task)

    def _postprocess_result(self, session_id: str, result_id: str) -> Artifact:
        data = self.agent.get_image_data(session_id, result_id)
        if data.error:
            return Artifact(parts=[{"type": "text", "text": data.error}])

        if data.mime_type and data.mime_type.startswith("image/"):
            return Artifact(parts=[
                FilePart(file=FileContent(
                    bytes=data.bytes.encode() if isinstance(data.bytes, str) else data.bytes,
                    mimeType=data.mime_type,
                    name=data.name or "generated_image.png"
                ))
            ])
        else:
            return Artifact(parts=[{"type": "text", "text": data.bytes or "[Empty text]"}])

    def _get_user_query(self, params: TaskSendParams) -> str:
        part = params.message.parts[0]
        if not isinstance(part, TextPart):
            raise ValueError("Only text parts are supported.")
        return part.text
