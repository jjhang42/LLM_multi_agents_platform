def taskgraph_to_reactflow(graph, tasks):
    """
    TaskGraph + Task dict 를 기반으로 React Flow 시각화용 노드/엣지 변환
    """
    nodes = []
    edges = []

    x_step = 200
    y_step = 120
    positions = {}

    for i, task_id in enumerate(graph.dependencies):
        task = tasks[task_id]
        label = f"{task.metadata.get('action', 'N/A')}\n{task.metadata.get('target', 'N/A')}"
        x = 100 + (i % 4) * x_step
        y = 100 + (i // 4) * y_step
        positions[task_id] = {"x": x, "y": y}

        nodes.append({
            "id": task_id,
            "data": { "label": label },
            "position": positions[task_id],
        })

    for target, sources in graph.dependencies.items():
        for source in sources:
            edges.append({
                "id": f"e_{source}_{target}",
                "source": source,
                "target": target
            })

    return { "nodes": nodes, "edges": edges }
