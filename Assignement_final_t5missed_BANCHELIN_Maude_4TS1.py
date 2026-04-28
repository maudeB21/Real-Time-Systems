#First do : gcc -fPIC -shared -o multiplication.so multiplication.c (if not already done)
#--> This command compiles the C code in multiplication.c into a shared library named multiplication.so,
#which can then be loaded and used in Python via ctypes. 


# In this code, tau5 (t5) is allowed to miss a deadline

import numpy as np
import pandas as pd

tasks = [
    {"id": 1, "C": 3.279784, "T": 10},
    {"id": 2, "C": 3, "T": 10},
    {"id": 3, "C": 2, "T": 20},
    {"id": 4, "C": 2, "T": 20},
    {"id": 5, "C": 2, "T": 40}, # T5 allowed to miss a dealine
    {"id": 6, "C": 2, "T": 40},
    {"id": 7, "C": 3, "T": 80},
]

Hyperperiod = 80
all_jobs = []


# For each task, we calculate how many instances (jobs) will be generated within the hyperperiod
# and create a list of all jobs with their arrival times and deadlines

for task in tasks:
    num_jobs = Hyperperiod // task["T"]
    for n in range(num_jobs):
        arrival = n * task["T"]
        deadline = arrival + task["T"]
        all_jobs.append({
            "task_id": task["id"],
            "C": task["C"],
            "arrival": arrival,
            "deadline": deadline,
            "completed": False,
            "instance": n + 1
        })

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
        earliest_next_arrival = remaining_jobs[0]["arrival"]
        for job in remaining_jobs:
            if job["arrival"] < earliest_next_arrival:
                earliest_next_arrival = job["arrival"]
        idle_time += (earliest_next_arrival - current_time) 
        current_time = earliest_next_arrival
        continue 
   
    # Separation of t5 from the rest of the ready jobs
    ready_not_t5 = []
    for job in ready_jobs:
        if job["task_id"] != 5:
            ready_not_t5.append(job)

    # If other tasks than t5 are ready, we choose among them (EDF)
    if len(ready_not_t5) > 0:
        selected_job = ready_not_t5[0]
        for job in ready_not_t5:
            if job["deadline"] < selected_job["deadline"]:
                selected_job = job
    else:
        # Otherwise, we can select t5 even if it misses its deadline
        selected_job = ready_jobs[0]
            
    # Timing Calculations
    start_time = current_time
    end_time = current_time + selected_job["C"]
    waiting_duration = start_time - selected_job["arrival"]

    is_on_time = end_time <= selected_job["deadline"]
    
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
    
    current_time = end_time
    remaining_jobs.remove(selected_job)

# Final schedule output
schedule_df = pd.DataFrame(final_schedule)
print(schedule_df.to_string(index=False))

# Global statistics
total_waiting_time = sum(item["Wait_Time"] for item in final_schedule)
print(f"\nTotal Waiting Time: {round(total_waiting_time, 4)}ms")
print(f"Total idle Time: {round(idle_time, 4)}ms")


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