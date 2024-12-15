from models.job import Job
from typing import List, Optional


def edf_priority(jobs: List[Job]) -> Optional[Job]:
    if len(jobs) == 0:
        return None
    # Sort active tasks by their absolute deadlines (earliest deadline first)
    return min(jobs, key=lambda job: job.deadline)  