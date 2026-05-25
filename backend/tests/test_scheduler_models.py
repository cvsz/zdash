from app.scheduler.models import JobStatus, JobType, ScheduleType, ScheduledJob


def test_scheduled_job_defaults():
    job = ScheduledJob(id='1', name='health', job_type=JobType.health_check, schedule_type=ScheduleType.manual)
    assert job.status == JobStatus.pending
    assert job.enabled is True
