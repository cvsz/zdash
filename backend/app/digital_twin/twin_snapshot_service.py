import hashlib
import json
from .models import TwinSnapshot


class TwinSnapshotService:
    def __init__(self, graph):
        self.graph = graph
        self._snaps = []

    def create_snapshot(self, org, ws, name):
        g = self.graph.build_graph(org, ws)
        c = hashlib.sha256(json.dumps(g, sort_keys=True).encode()).hexdigest()
        s = TwinSnapshot(
            id=f"snap-{len(self._snaps) + 1}",
            organization_id=org,
            workspace_id=ws,
            name=name,
            node_count=len(g["nodes"]),
            edge_count=len(g["edges"]),
            summary="snapshot",
            checksum=c,
        )
        self._snaps.append(s)
        return s

    def list_snapshots(self, org, ws):
        return [
            s for s in self._snaps if s.organization_id == org and s.workspace_id == ws
        ]

    def compare_snapshots(self, a, b):
        return {
            "node_delta": b.node_count - a.node_count,
            "edge_delta": b.edge_count - a.edge_count,
        }

    def verify_snapshot_checksum(self, snapshot, checksum):
        return snapshot.checksum == checksum
