import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, Literal

from writer.core import Config
from writer.keyvalue_storage import writer_kv_storage

if TYPE_CHECKING:
    from writer.blueprints import Graph


logger = logging.getLogger("journal")

JOURNAL_KEY_PREFIX = "wf-journal-"


class JournalRecord:
    def __init__(
        self,
        execution_environment: Dict,
        title: str,
        graph: "Graph"
    ):
        self.started_at = datetime.now(timezone.utc)
        self.instance_type = "editor" if Config.mode == "edit" else "agent"

        self.trigger = {
            "event": execution_environment.get("context", {}).get("event"),
            "component": {}
        }

        if self.trigger["event"] == "wf-run-blueprint":
            self.trigger["component"]["type"] = "blueprint"
            self.trigger["component"]["id"] = graph.nodes[0].component.parentId
        else:
            self.trigger["component"]["type"] = "block"
            self.trigger["component"]["id"] = graph.get_start_nodes()[0].id

        if "API" in title:
            self.trigger["type"] = "API"
        elif "Cron" in title:
            self.trigger["type"] = "Cron"
        elif "UI" in title:
            self.trigger["type"] = "UI"
        else:
            self.trigger["type"] = "On demand"

        self.graph = graph

    def to_dict(self) -> Dict[str, Any]:
        block_outputs = {}
        for graph_node in self.graph.nodes:
            block_outputs[graph_node.id] = {"result": graph_node.result, "outcome": graph_node.outcome}
        return {
            "timestamp": self.started_at.isoformat(),
            "instanceType": self.instance_type,
            "trigger": self.trigger,
            "blockOutputs": block_outputs,
        }

    def construct_key(self) -> str:
        return f"{JOURNAL_KEY_PREFIX}{self.instance_type[0]}-{int(self.started_at.timestamp() * 1000)}"
    
    def save(self, result: Literal["success", "error", "stopped"]) -> None:
        if "journal" not in Config.feature_flags or not writer_kv_storage.is_accessible():
            return
        data = self.to_dict()
        data["result"] = result
        writer_kv_storage.save(self.construct_key(), data)
