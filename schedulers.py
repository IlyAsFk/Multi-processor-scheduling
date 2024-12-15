from models.job import Job
from models.task import Task
from typing import List, Optional


def edf_priority(jobs: List[Job]) -> Optional[Job]:
    if len(jobs) == 0:
        return None
    # Sort active tasks by their absolute deadlines (earliest deadline first)
    return min(jobs, key=lambda job: job.deadline)  

def global_edf_scheduler(queue: list[Job], m: int) -> list[Job]:
    """
    Sélectionne les m jobs avec les deadlines les plus proches pour m processeurs.
    Args:
    - queue: Liste des jobs disponibles
    - m: Nombre de processeurs
    
    Returns:
    Liste des m jobs élus pour exécution
    """
    if not queue:
        return []
    
    # Trier les jobs par deadline 
    sorted_jobs = sorted(queue, key=lambda job: job.deadline)
    
    # Sélectionner les m premiers jobs (ou moins si queue < m)
    elected_jobs = sorted_jobs[:m]
    
    return elected_jobs

def edf_k_scheduler(tasks: List[Task], m: int, k:int):
    """
    Assigner aux k-1 taches aveSc le plus d'utilisation la priorité maximale.
    Modifie la liste des tâches donnée en reférence
    Args:
    - tasks: Objet contenant une liste des taches
    - m: Nombre de processeurs
    - k : the number of tasks to give the priority to
    """
    
    if not tasks:
        return []
    # Trier par ordre décroissant les tâches selon leur utilisation
    tasks.sort(key=lambda task: task.utilisation, reverse=True)
    # Donner la priorité maximale aux jobs des k-1 premières tâches
    for task in tasks[:k-1]: task.deadline = -math.inf