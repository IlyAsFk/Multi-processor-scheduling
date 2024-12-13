
import sys
from partitioner import *
from models.taskset import TaskSet
from models.task import Task
import csv
from typing import List

# GLOBAL CONSTANTS
SCHEDULABLE_WITH_SIMULATION = 0
SCHEDULABLE_WITHHOUT_SIMULATION = 1
NOT_SCHEDULABLE_WITH_SIMULATION = 2
NOT_SCHEDULABLE_WITHOUT_SIMULATION = 3 # necessary condition failure 
CANNOT_TELL = 4 

def schedule(tasks, nb_cores, scheduler, heuristic, sort):
	tasks = taskset.tasks
	# partition tasks between different cores 
	partitioned, partitionable = partition(tasks, sort, heuristic, nb_cores)

	cores = []

	for core in partitioned: # partitioned contient pr chq core, une liste de taches
		# Au d'avoir slt le nb de tâche, on récupère l'objet entier
		processor = [task for task_number in core for task in tasks if task.get_task_number() == task_number]
		cores.append(processor)

	partitioned = cores

	if partitionable:

		process_number = 1

		for core in partitioned:

			# determine if sks are synchronous
			synchronous = if_synchronous(core)

			has_implicit_deadlines = has_implicit_deadlines(core)
			# # determine if tasks have constrained deadlines

			# if scheduler == 'rm' or scheduler == 'dm':
			# 	constrained_deadlines = if_constrained_deadlines(core)
			# 	if not synchronous and not constrained_deadlines: 
			# 		print("COMBINATION NOT SUPPORTED" + "\n")
			# 		return(COMBINATION_NOT_SUPPORTED)

			# feasibility_interval
			
			# if scheduler == 'rm' or scheduler == 'dm':

			# 	if synchronous and constrained_deadlines: 
			# 		schedulable = task_utilization(core)
			# 		if schedulable: interval = worst_response_time(core)

			# 	elif synchronous and not constrained_deadlines:
			# 		schedulable = task_utilization(core)
			# 		if schedulable : interval = feasibility_interval(core)

			# 	elif not synchronous and constrained_deadlines:
			# 		schedulable = True
			# 		interval    = m_asynchronous_feasibility(core)

			# identify the smallest feasibility interval

			# A sporadic implicit-deadline taskset 𝜏 is schedulable using ffdu
			# --> Faut check qu'on est en synchrone ?
			if (scheduler == 'partitioned' and has_implicit_deadlines and heuristic=="ff" and sort=="du"):
				if(is_schedulable_partitioned_edf(tasks,nb_cores)): # check sufficient condition
					return True
			elif (scheduler == 'global' and has_implicit_deadlines and synchronous):
                # necessary & sufficient condition
				# Si th 90 ok alors exit schedulable (c du periodic) sinon (pt ê on a du periodic ou sporadic) test th 91 (peut traiter les 2)
				# Si th 91 ok exit schedulable (c du sporadic) sinon simul
				# Compute U_max and system utilization
				u_max = compute_u_max(tasks)
				system_utilization = compute_system_utilization(tasks)
				if(is_schedulable_periodic_global_edf(nb_cores,u_max,system_utilization)
					or is_schedulable_sporadic_global_edf(nb_cores,u_max,system_utilization)):
					return SCHEDULABLE_WITHHOUT_SIMULATION
			else: # edf(k)
				# Check if there are at least k tasks
				if len(core) < scheduler: 
					print("The task set must have at least k tasks.")
					return CANNOT_TELL
                if has_implicit_deadlines and edf_k_test_with_given_m(tasks,nb_cores,scheduler):
					return SCHEDULABLE_WITHHOUT_SIMULATION
			# if scheduler == 'edf':
			# 	if synchronous:
			# 		#check cours/projet uni 
			# 		interval = feasibility_interval(core)

			# 	else: 
			# 		#check cours multi
			# 		interval    = edf_asynchronous_feasibility(core)
			# 		schedulable = True

			#check if there's not SUFFICIENT condition to decide schedulability

			if schedulable: # necessary condition are met

				# simulation 

				print("Process " + str(process_number) + "\n")
				print("Feasibility interval is [ 0,", interval, ")")

				process_number += 1

				if simulate(scheduler, interval, core, len(tasks)):
					print("NOT SCHEDULABLE WITH SIMULATION" + "\n")
					return(NOT_SCHEDULABLE_WITH_SIMULATION)

				print("\n")

			else: 
				print("NOT SCHEDULABLE WITHOUT SIMULATION" + "\n")
				return(NOT_SCHEDULABLE_WITHOUT_SIMULATION)

		print("SCHEDULABLE" + "\n")
		return(SCHEDULABLE)

	else: 
		print("PARTITIONING FAILS" + "\n")
		return(NOT_SCHEDULABLE_WITHOUT_SIMULATION)
	
def parse_task_file(file_path: str) -> List[Task]:
    tasks = []
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for line_number, row in enumerate(reader, start=1):
            offset, computation_time, deadline, period = map(int, row)
            tasks.append(Task(line_number,offset, computation_time, deadline, period))
            
    taskset = TaskSet(tasks)
    return taskset 

def if_synchronous(tasks):

	offset = None

	for task in tasks:

		if offset == None:
			offset = task.get_offset()

		else:
			if task.get_offset() != offset:
				return False

	return True

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

def is_schedulable_partitioned_edf(tasks, m):
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

def is_schedulable_sporadic_global_edf(m,u_max,system_utilization):
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

def edf_k_test_with_given_m(task_set, k, m):
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
    task_utilizations = [C / T for C, T in task_set]
    
    # Sort tasks by utilization in descending order
    task_utilizations.sort(reverse=True)
    
    # Calculate U(k) and U(k+1) 
    U_k = task_utilizations[k-1]  # Utilization of the k-th task (0-indexed)
    
	# Compute U(τ^(k+1)) as the sum of the (n-k-1) lowest utilizations
    n = len(task_utilizations)
    U_k_plus_1 = sum(task_utilizations[:n - k - 1])
    
    # Check the test condition from Theorem 93
    schedulable = m == ((k - 1) + (U_k_plus_1 / (1 - U_k)))

    return schedulable



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