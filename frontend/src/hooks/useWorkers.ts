import { useState, useEffect } from "react";
import { getQueueStatus, listTasks, enqueueTask } from "../api/endpoints";
import type { QueueStatus, TaskItem } from "../api/types";

export function useWorkers() {
  const [queueStatus, setQueueStatus] = useState<QueueStatus[]>([]);
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    let mounted = true;
    const fetchData = async () => {
      setLoading(true);
      try {
        const qs = await getQueueStatus();
        const tlist = await listTasks();
        if (mounted) {
          setQueueStatus(qs);
          setTasks(tlist);
        }
      } catch (err) {
        console.error("Failed to fetch workers data:", err);
      } finally {
        if (mounted) setLoading(false);
      }
    };
    fetchData();
    return () => {
      mounted = false;
    };
  }, [refreshKey]);

  const refresh = () => setRefreshKey((k) => k + 1);

  const enqueue = async (type: string, payload?: Record<string, unknown>) => {
    await enqueueTask({ type, payload });
    refresh();
  };

  return { queueStatus, tasks, loading, refresh, enqueue };
}
