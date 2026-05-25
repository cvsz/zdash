def render_metrics() -> str:
    return '\n'.join([
        'zdash_requests_total 0',
        'zdash_request_latency_ms 0',
        'zdash_errors_total 0',
        'zdash_events_total 0',
        'zdash_scheduler_jobs_total 0',
        'zdash_risk_halt_active 0',
        'zdash_backtests_total 0',
        'zdash_content_items_total 0',
        'zdash_iot_actions_total 0',
    ])
