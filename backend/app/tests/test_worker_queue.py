from app.workers.queue import queue
from app.tenancy.tenant_context import TenantContext

def test_queue_lifecycle():
    t=queue.enqueue('custom',{},TenantContext('o1','w1'))
    got=queue.dequeue('w')
    assert got and got.id==t.id
    queue.complete(t.id,{"ok":True})
    assert queue.list_tasks('o1','w1')[0].status=='completed'
