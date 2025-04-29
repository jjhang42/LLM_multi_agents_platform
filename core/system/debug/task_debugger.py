# core/system/debug/task_debugger.py

from typing import Dict
from core.system.metadata.task_graph import TaskGraph

def debug_print_tasks_and_graph(tasks: Dict[str, dict], graph: TaskGraph):
    print("\n====== [Task List] ======")
    for task_id, task_data in tasks.items():
        print(f"- {task_id}:")
        for key, value in task_data.items():
            print(f"    {key}: {value}")
    print("\n====== [TaskGraph Dependencies] ======")
    for task_id, depends in graph.dependencies.items():
        print(f"- {task_id} depends on {depends}")

    print("\n====== [TaskGraph Completed] ======")
    print(list(graph.completed))
    print("===============================\n")
