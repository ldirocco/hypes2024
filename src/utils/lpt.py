def lpt_scheduling(jobs, num_machines):
    """
    Longest Processing Time (LPT) Scheduling Algorithm
    """
    # Sort jobs by processing time in descending order
    sorted_jobs = sorted(jobs, reverse=True)
    
    # Initialize schedule for each machine
    schedule = [[] for _ in range(num_machines)]
    
    # Distribute jobs to machines based on LPT
    for job in sorted_jobs:
        # Find machine with minimum total processing time
        min_machine = min(schedule, key=lambda x: sum([job_time for _, job_time in x]))
        
        # Assign job to the machine with the minimum total processing time
        min_machine.append(job)
    
    return schedule