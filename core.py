from models import TaskSet, Job
from schedulers import edf_priority,global_edf_scheduler,edf_k_scheduler
import math 
# constant-step simulator
def simulate_local(taskset: TaskSet, t_max: int):
    current_task=1  
    queue: list[Job] = []
    for t in range(t_max + 1):
        # Release new jobs
        queue+=taskset.release_jobs(t)
        # Check for deadlines
        for job in queue:
            if job.deadline_missed(t):
                #print(f"Deadline missed for {job} at time {t} !")
                return 2 # The task set is not schedulable and you had to simulate the execution.
        elected_job = edf_priority(queue)
        if elected_job is not None:
            elected_job.schedule(1)
            if elected_job.is_complete():
                #print("complete ;",elected_job)
                queue.remove(elected_job)
    return 0    # The task set is schedulable and you had to simulate the 
    
def simulate_global(taskset:TaskSet, m: int, scheduler, t_max: int):
    """
    Simulation d'un ordonnancement global EDF sur m processeurs
    
    Args:
    - taskset: Ensemble des tâches
    - m: Nombre de processeurs
    - scheduler: Fonction de sélection des jobs
    - t_max: Temps maximum de simulation
    
    Returns:
    0 si ordonnançable, 2 sinon
    """
    queue: list[Job] = []
    processor_load: list[Job] = [None] * m  # États des m processeurs
    # the scheduler gives k as a parameter for edf-k
    # edf(k=1) is a particular case -> do global scheduling 
    if isinstance(scheduler, int) and k!=1: 
        edf_k_scheduler(taskset.tasks, m, k)        
    for t in range(t_max + 1):
        # Libérer les nouveaux jobs
        queue += taskset.release_jobs(t)
        
        # Vérifier les deadlines
        for job in queue:
            if job.deadline_missed(t):
                return 2  # Non ordonnançable
        
        # Libérer les processeurs ayant terminé leurs jobs
        for i in range(m):
            if processor_load[i] and processor_load[i].is_complete():
                queue.remove(processor_load[i])
                processor_load[i] = None
        
        # Sélectionner les jobs pour les processeurs disponibles
        elected_jobs = global_edf_scheduler(queue, m)
        
        # Assigner les jobs aux processeurs
        # Un core traite un job à la fois à chq instant t 
        for job in elected_jobs:
            for i in range(m):
                if processor_load[i] is None or job.deadline < processor_load[i].deadline:
                    processor_load[i] = job
                    job.schedule(1) 
                    break
    
    return 0  # Ordonnançable