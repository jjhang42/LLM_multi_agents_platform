# core/system/parser/task_assembler.py

from typing import Dict, Tuple, List
from core.system.metadata.task_graph import TaskGraph
from core.system.formats.a2a import Task

def assemble_tasks_with_graph(tasks: List[Task]) -> Tuple[Dict[str, Task], TaskGraph]:
    """
    A2A Task 리스트로부터 Task 딕셔너리와 TaskGraph를 생성합니다.
    - Task.metadata["depends"] 필드를 기준으로 DAG(Directed Acyclic Graph)를 구성합니다.

    Args:
        tasks (List[Task]): LLM에서 생성된 Task 객체 리스트

    Returns:
        Tuple[Dict[str, Task], TaskGraph]: task_id 기준의 딕셔너리, 종속성 그래프
    """
    task_dict: Dict[str, Task] = {}
    graph = TaskGraph()

    for task in tasks:
        task_id = task.id
        task_dict[task_id] = task

        # ✅ depends는 metadata에만 존재 (정식 A2A 확장 규칙)
        depends_raw = task.metadata.get("depends") if task.metadata else []
        
        if isinstance(depends_raw, str):
            depends = [depends_raw]
        elif isinstance(depends_raw, list):
            depends = depends_raw
        else:
            depends = []

        graph.add_task(task_id, depends)

    return task_dict, graph
