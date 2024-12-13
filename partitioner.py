from operator import itemgetter


"""
    Do the next fit or the first fit

    tasks_utilisation : list, [task utilisation, task number]
    heuristic :         str, chosen heuristic
    nb_cores :          int,  number of cores

    return [[tasks numbers]], bool 
"""
def first_next_fit(tasks_utilisation, heuristic, nb_cores):

    cores             = [[] for i in range(nb_cores)] # Each core have a list of tasks to execute
    cores_utilisation = [0  for i in range(nb_cores)]
    partitionable     = True
    next_core         = 0

    for task_utilisation in tasks_utilisation: # on parcourt chq tache

        partitionable = False

        for i in range(next_core, len(cores)): # on rg dans quel core, on peut placer la tache courante 

            if cores_utilisation[i] + task_utilisation[0] <= 1: # faut pas qu'avec la tache, on dépasse 1

                cores_utilisation[i] += task_utilisation[0]
                cores[i].append(task_utilisation[1])
                partitionable = True
                break

        if partitionable == False: break

        if heuristic == 'nf': next_core = i

    return cores, partitionable


"""
    Do the best fit or the worst fit

    tasks_utilisation : list, [task utilisation, task number]
    heuristic :         str, chosen heuristic
    nb_cores :          int,  number of cores

    return [[tasks numbers]], bool 
"""
def best_worst_fit(tasks_utilisation, heuristic, nb_cores):

    cores             = [[] for i in range(nb_cores)]
    cores_utilisation = [0  for i in range(nb_cores)]
   
    for task_utilisation in tasks_utilisation:

        best_core = None

        for i in range(len(cores)):

            core_utilisation = cores_utilisation[i] + task_utilisation[0]

            if core_utilisation <= 1:
                # We maximise the load of the cores
                if heuristic == 'bf' and (best_core == None or core_utilisation > (cores_utilisation[best_core] + task_utilisation[0])):
                    best_core = i
                # We minimise the load of the cores 
                elif heuristic == 'wf' and (best_core == None or core_utilisation < (cores_utilisation[best_core] + task_utilisation[0])): 
                    best_core = i

        if best_core == None: return cores, False # The current task cannot be assigned in any core
           
        else: 
            cores_utilisation[best_core] += task_utilisation[0]
            cores[best_core].append(task_utilisation[1])
            
    return cores, True
            

"""
    partition a list of task

    tasks     : list, tasks
    sort      : str,  indicate if we sort by increasing or decreasing
    heuristic : str,  chosen heuristic
    nb_cores  : int,  number of cores

    return [[tasks numbers]], bool
"""
def partition(tasks, sort, heuristic, nb_cores):

    # built a list with the pair [task utilisation, task number] 
    tasks_utilisation = [ [tasks[i].get_utilisation(), tasks[i].get_task_number()] for i in range(len(tasks)) ]

    # sort tasks by increasing or decreasing utilisation
    if   sort == 'du': tasks_utilisation = sorted(tasks_utilisation, key=itemgetter(0), reverse=True)
elif sort == 'iu': tasks_utilisation = sorted(tasks_utilisation, key=itemgetter(0), reverse=False)

    # do the desired heuristic
    if   heuristic == 'ff': partitioned, partitionable = first_next_fit(tasks_utilisation, heuristic, nb_cores)
    elif heuristic == 'nf': partitioned, partitionable = first_next_fit(tasks_utilisation, heuristic, nb_cores)
    elif heuristic == 'wf': partitioned, partitionable = best_worst_fit(tasks_utilisation, heuristic, nb_cores)
    elif heuristic == 'bf': partitioned, partitionable = best_worst_fit(tasks_utilisation, heuristic, nb_cores)

    return partitioned, partitionable