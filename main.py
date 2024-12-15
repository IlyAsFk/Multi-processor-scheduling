
import sys
from partitioner import *
from models.taskset import TaskSet
from models.task import Task
import csv
from typing import List
from core import simulate_local, simulate_global

# GLOBAL CONSTANTS
SCHEDULABLE_WITH_SIMULATION = 0
SCHEDULABLE_WITHOUT_SIMULATION = 1
NOT_SCHEDULABLE_WITH_SIMULATION = 2
NOT_SCHEDULABLE_WITHOUT_SIMULATION = 3 # necessary condition failure 
CANNOT_TELL = 4 


def schedule_partitioned_edf(taskset, nb_cores, heuristic, sort):
    tasks = taskset.tasks
    # A sporadic implicit-deadline taskset 𝜏 is schedulable using ffdu
    if heuristic == "ff" and sort == "du":
        # TH 78. check sufficient condition using EDF as local scheduler
        if has_implicit_deadlines(tasks) and partitioned_edf_shorcut(tasks, nb_cores): 
            return True
    feasibility_interval=0
    # partition tasks between different cores 
    partitioned, partitionable = partition(tasks, sort, heuristic, nb_cores)
    cores = [] # Liste de liste de tâches
    for core in partitioned:  # partitioned contient pr chq core, une liste de taches
        # Au d'avoir slt le nb de tâche, on récupère l'objet entier
        processor = [task for task_number in core for task in tasks if task.get_task_number() == task_number]
        cores.append(TaskSet(processor)) # Create a sub-taskset for each core
    partitioned = cores
    
    if partitionable:
        for core in partitioned:
            tasks=core.tasks
            return simulate_local(tasks,feasibility_interval)
    else:
        print("PARTITIONING FAILS" + "\n")
        return 3

def schedule(taskset, nb_cores, scheduler, heuristic, sort):
    tasks = taskset.tasks
    if scheduler == "partitionned":
        exit = schedule_partitioned_edf(taskset, nb_cores, heuristic, sort)
    elif scheduler == "global":
        # TH.91 : sufficient condition using global EDF
        if has_implicit_deadlines(tasks):
            u_max = compute_u_max(tasks)
            system_utilization = compute_system_utilization(tasks)
            if global_edf_shorcut(nb_cores, u_max, system_utilization):
                return SCHEDULABLE_WITHOUT_SIMULATION
        k = 1  # run the simulation for global scheduling using edf(k=1)
        feasibility_interval = 0
    else:  # edf(k)
        k = scheduler
        if k > len(tasks):
            print("The task set must have at least k tasks.")
            return CANNOT_TELL
        # TH.93 : sufficient condition using EDF^(k)
        if has_implicit_deadlines and edf_k_shorcut(tasks, nb_cores, k):
            return SCHEDULABLE_WITHOUT_SIMULATION
        feasibility_interval = 0

    exit = simulate_global(taskset, nb_cores, k, feasibility_interval)
    if exit == 0:
        return SCHEDULABLE_WITH_SIMULATION
    elif exit == 2:
        return SCHEDULABLE_WITHOUT_SIMULATION
    elif exit == 3:
        return NOT_SCHEDULABLE_WITHOUT_SIMULATION


def parse_task_file(file_path: str) -> TaskSet:
    tasks = []
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for line_number, row in enumerate(reader, start=1):
            offset, computation_time, deadline, period = map(int, row)
            tasks.append(Task(line_number,offset, computation_time, deadline, period))
            
    taskset = TaskSet(tasks)
    return taskset 

def compute_u_max(tasks):
    """
    Computes the maximum utilization of any task.
    """
    return max(C / T for C, T, _ in tasks)

def compute_system_utilization(tasks):
    """
    Computes the total system utilization.
    """
    return sum(C / T for C, T, _ in tasks)

def has_implicit_deadlines(tasks):
    """
    Checks if ALL tasks in the task set have implicit deadlines.

    Returns:
        bool: True if all tasks have D == T, False otherwise.
    """
    for _, T, D in tasks:
        if D != T:
            return False
    return True

def partitioned_edf_shorcut(tasks, m):
    """
    Determines if a task set is schedulable using partitioned EDF based on the theorem.

    Returns:
        bool: True if the task set is schedulable, False if the condition isn't respected
    """
    # Compute U_max and U(τ)
    u_max = compute_u_max(tasks)
    system_utilization = compute_system_utilization(tasks)
    
    # Apply the schedulability conditions
    if u_max > 1:
        return False
    if system_utilization > (m + 1) / 2:
        return False
    
    return True

def is_schedulable_periodic_global_edf(m,u_max,system_utilization):
    """
    Determines if a task set is schedulable using global EDF 
    based on the theorem for the periodic case.

    Returns:
        bool: True if the task set is schedulable, False otherwise.
    """
    # Apply the schedulability conditions for the periodic case
    if u_max <= 1 and system_utilization <= m:
        return True

    return False

def global_edf_shorcut(m,u_max,system_utilization):
    """
    Determines if a task set is schedulable using global EDF 
    based on the theorem for the sporadic case.

    Returns:
        bool: True if the task set is schedulable, False otherwise.
    """    
    # Apply the schedulability conditions for the sporadic case
    if system_utilization <= m - (m - 1) * u_max:
        return True
        
    return False

def edf_k_shorcut(tasks, m, k):
    """
    Checks if a sporadic implicit-deadline system is schedulable using EDF^(k) on m processors.
    
    Parameters:
    - task_set: List of tasks, where each task is represented as a tuple (C, T) 
                (C: computation time, T: period).
    - k: Level of EDF (k).
    - m: Number of processors.
    
    Returns:
    - is_schedulable: True if schedulable, False otherwise.
    """
    # Compute the utilizations of each task
    task_utilizations = [C / T for C, T in tasks]
    
    # Sort tasks by utilization in descending order
    task_utilizations.sort(reverse=True)
    
    # Calculate U(k) and U(k+1) 
    U_k = task_utilizations[k-1]  # Utilization of the k-th task (0-indexed)
    
	# Compute U(τ^(k+1)) as the sum of the (n-k-1) lowest utilizations
    n = len(task_utilizations)
    U_k_plus_1 = sum(task_utilizations[:n - k - 1])
    
    # Check the test condition from Theorem 93
    return m == ((k - 1) + (U_k_plus_1 / (1 - U_k)))



if __name__ == '__main__':

	name_file = sys.argv[1]
	heuristic = 'ff'
	sort = 'du'
	nb_cores = int(sys.argv[2])

	for i in range(2, len(sys.argv), 2):
		if sys.argv[i] == '-v' : scheduler = sys.argv[i+1] # could be a string or reprensent the <k> value for edf_k
		elif sys.argv[i] == '-w' : worker = sys.argv[i+1] # Check if it's a number
		elif sys.argv[i] == '-h' : heuristic = sys.argv[i+1]
		elif sys.argv[i] == '-s' : sort = sys.argv[i+1]

	# build list of task 
	taskset = parse_task_file(name_file)
	
	exit(schedule(taskset, nb_cores, scheduler, heuristic, sort))