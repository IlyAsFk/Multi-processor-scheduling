from dataclasses import dataclass
from .task import Task
from .job import Job
from typing import List

@dataclass
class TaskSet:
    tasks: list[Task]

    def release_jobs(self, t: int) -> list[Job]:
        jobs = []
        for task in self.tasks:
            if t % task.period == 0:
                job = task.spawn_job(t)
                if  job != None :
                    jobs.append(job)
        return jobs
    
    def read_file(name_file):
        with open(name_file) as f :
            tasks = []
            task_number = 1

            for line in f:
                task = line.strip().split()
                tasks.append(Task(int(task[0]), int(task[1]), int(task[2]), int(task[3]), task_number))
                task_number += 1
        taskset = TaskSet(tasks)
        return tasks