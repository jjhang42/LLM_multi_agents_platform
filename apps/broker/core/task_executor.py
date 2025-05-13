from core.system.formats.a2a import Task, TaskGraphPayload, TaskSendResult
from core.system.metadata.task_graph import TaskGraph
from broker.core.executor_runner import ExecutorRunner

from typing import Dict, List

async def execute_task_graph(payload: TaskGraphPayload, runner: ExecutorRunner) -> TaskSendResult:
    task_dict: Dict[str, Task] = payload.tasks
    graph = TaskGraph.deserialize({"dependencies": payload.graph})
    completed_results: List[dict] = []

    print("🧩 [Broker] 실행 시작")
    print("📦 전체 task ID 목록:", list(task_dict.keys()))
    print("🔗 의존성 그래프 (graph.dependencies):", graph.dependencies)

    if graph.has_cycle():
        raise ValueError("🚫 순환 의존성이 있는 TaskGraph입니다. 실행할 수 없습니다.")

    while not graph.is_all_completed():
        executable_ids = graph.get_executable_tasks()
        print("🧮 실행 가능한 Task 목록:", executable_ids)
        print("✅ 완료된 Task:", list(graph.completed))

        if not executable_ids:
            raise RuntimeError("❌ 실행 가능한 Task가 없습니다. DAG 상태를 확인하세요.")

        tasks_to_run = [task_dict[tid] for tid in executable_ids]
        print(f"[Broker] 실행 중인 Task: {[t.id for t in tasks_to_run]}")

        results = await runner.run_tasks(tasks_to_run)
        completed_results.extend(results)

        for task in tasks_to_run:
            print(f"🟩 Task 완료됨: {task.id}")
            graph.mark_completed(task.id)

    print("🎉 모든 Task 실행 완료")
    return TaskSendResult(
        status="broker_executed",
        context_id=payload.context_id,
        message=f"{len(completed_results)} tasks executed in DAG order.",
        results=completed_results
    )
