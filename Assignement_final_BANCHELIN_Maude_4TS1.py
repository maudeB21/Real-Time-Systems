#First do : gcc -fPIC -shared -o multiplication.so multiplication.c (if not already done)
#--> This command compiles the C code in multiplication.c into a shared library named multiplication.so,
#which can then be loaded and used in Python via ctypes. 

import numpy as np
import pandas as pd


tasks = [
    {"id": 1, "C": 3.279784, "T": 10}, # C1 founded on the WCET measured in the previous part (WCET_BANCHELIN_Maude.py)
    {"id": 2, "C": 3, "T": 10},
    {"id": 3, "C": 2, "T": 20},
    {"id": 4, "C": 2, "T": 20},
    {"id": 5, "C": 2, "T": 40}, # T5 not allowed to miss a dealine
    {"id": 6, "C": 2, "T": 40},
    {"id": 7, "C": 3, "T": 80},
]

Hyperperiod = 80 # LCM of the periods (10, 20, 40, 80) to ensure we cover a complete cycle of all tasks

all_jobs = []


# For each task, we calculate how many instances (jobs) will be generated within the hyperperiod
# and create a list of all jobs with their arrival times and deadlines
for task in tasks: 
    num_jobs = Hyperperiod//task["T"]
    for n in range(num_jobs):
        arrival = n * task["T"]
        deadline = arrival + task["T"]
        
        # Jobs infos :
        all_jobs.append({
            "task_id": task["id"],
            "C": task["C"],
            "arrival": arrival,
            "deadline": deadline,
            "completed": False,
            "instance": n + 1
        })
                    
# We sort the jobs by their arrival time for the scheduling process     
all_jobs.sort(key=lambda x: x["arrival"])

print(f"Jobs generated for the hyperperiod of {Hyperperiod} ms : {len(all_jobs)} jobs")

# Scheduling using Earliest Deadline First (EDF) algorithm
current_time = 0
final_schedule = []
remaining_jobs = list(all_jobs)  
idle_time = 0

while len(remaining_jobs) > 0:
    # Identifying jobs that have arrived and are ready to be processed
    ready_jobs = []
    for job in remaining_jobs:
        if job["arrival"] <= current_time:
            ready_jobs.append(job)
    
    # If no jobs are ready, jump the clock to the next available arrival
    if len(ready_jobs) == 0: 
        # Earliest deadline first (EDF)
        earliest_next_arrival = remaining_jobs[0]["arrival"]
        for job in remaining_jobs:
            if job["arrival"] < earliest_next_arrival:
                earliest_next_arrival = job["arrival"]
        idle_time += (earliest_next_arrival - current_time) 
        current_time = earliest_next_arrival
        continue 

    # We pick the job from the ready list that has the smallest deadline value
    selected_job = ready_jobs[0]
    for job in ready_jobs:
        if job["deadline"] < selected_job["deadline"]:
            selected_job = job
            
    # Timing Calculations
    start_time = current_time
    end_time = current_time + selected_job["C"]
    waiting_duration = start_time - selected_job["arrival"]

    
    # Checking if the deadline is met
    is_on_time = end_time <= selected_job["deadline"]
    
    # Record the results
    final_schedule.append({
        "Task": f"T{selected_job['task_id']}, J{selected_job['instance']}",
        "Instance": selected_job["instance"],
        "Start": round(start_time, 4),
        "End": round(end_time, 4),
        "Deadline": selected_job["deadline"],
        "Wait_Time": round(waiting_duration, 4),
        "idle_Time": round(idle_time, 4),
        "Status": "SUCCESS" if is_on_time else "MISSED DEADLINE"
    })
    
    # Update state for the next iteration
    current_time = end_time
    remaining_jobs.remove(selected_job)

# Displaying the final schedule in a clear table
schedule_df = pd.DataFrame(final_schedule)
print(schedule_df)

# Summary of results
total_waiting_time = sum(item["Wait_Time"] for item in final_schedule)
print(f"\nTotal Waiting Time: {total_waiting_time}ms")
print(f"\nTotal idle Time: {idle_time}ms")


# Response time analysis (Rij) for each job
print("\n--- Response Time analysis (Rij) ---")

verif_data = []
for i in range(len(final_schedule)):
    job = final_schedule[i]
    

    arrival_time = all_jobs[i]["arrival"] # Corresponding arrival time from the original job list
    response_time = job["End"] - arrival_time
    
    deadline = job["Deadline"]
    is_schedulable = response_time <= (deadline - arrival_time)
    
    verif_data.append({
        "Task": job["Task"],
        "R_ij (Response Time)": round(response_time, 4),
        "Max Allowed (T_i)": deadline - arrival_time,
        "Schedulable?": "OK" if is_schedulable else "LATE"
    })

verif_df = pd.DataFrame(verif_data)
print(verif_df.to_string(index=False))