from collections import deque

# Basic Process class to store all process info
class Process:
    def __init__(self, name, arrival_time, burst_time, priority=0):
        self.name = name
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.priority = priority
        self.remaining_time = burst_time
        self.completion_time = 0
        self.waiting_time = 0
        self.turnaround_time = 0

# --- CPU SCHEDULING ---

def sjf_scheduling(processes):
    # Sort by arrival time first
    processes = sorted(processes, key=lambda p: p.arrival_time)
    time = 0
    
    for p in processes:
        # If process hasn't arrived, wait for it
        if time < p.arrival_time:
            time = p.arrival_time
        time += p.burst_time
        p.completion_time = time
        p.turnaround_time = p.completion_time - p.arrival_time
        p.waiting_time = p.turnaround_time - p.burst_time
    
    return processes

def non_preemptive_priority(processes):
    # Same logic as SJF but with priority sorting
    processes = sorted(processes, key=lambda p: p.arrival_time)
    time = 0
    
    for p in processes:
        if time < p.arrival_time:
            time = p.arrival_time
        time += p.burst_time
        p.completion_time = time
        p.turnaround_time = p.completion_time - p.arrival_time
        p.waiting_time = p.turnaround_time - p.burst_time
    
    return processes

def preemptive_priority(processes):
    # This one switches between processes based on priority
    processes = sorted(processes, key=lambda p: p.arrival_time)
    time = 0
    completed = []
    
    while len(completed) < len(processes):
        # Find processes that have arrived and not finished
        ready = [p for p in processes if p.arrival_time <= time and p.remaining_time > 0]
        
        if not ready:
            time = min(p.arrival_time for p in processes if p.remaining_time > 0)
            continue
        
        # Pick highest priority (lowest number)
        current = min(ready, key=lambda x: x.priority)
        time += 1
        current.remaining_time -= 1
        
        if current.remaining_time == 0:
            current.completion_time = time
            current.turnaround_time = current.completion_time - current.arrival_time
            current.waiting_time = current.turnaround_time - current.burst_time
            completed.append(current)
    
    return processes

def round_robin_scheduling(processes, quantum=2):
    # Use queue for round robin
    q = deque()
    time = 0
    processes = sorted(processes, key=lambda p: p.arrival_time)
    idx = 0
    
    if processes:
        q.append(processes[0])
        idx = 1
    
    while q or idx < len(processes):
        # Add newly arrived processes
        while idx < len(processes) and processes[idx].arrival_time <= time:
            q.append(processes[idx])
            idx += 1
        
        if not q:
            time = processes[idx].arrival_time
            continue
        
        p = q.popleft()
        
        if p.remaining_time <= quantum:
            time += p.remaining_time
            p.remaining_time = 0
            p.completion_time = time
            p.turnaround_time = p.completion_time - p.arrival_time
            p.waiting_time = p.turnaround_time - p.burst_time
        else:
            time += quantum
            p.remaining_time -= quantum
            q.append(p)  # back to queue
    
    return processes

# --- PAGING ---

def fifo_paging(num_frames, page_seq):
    # FIFO removes oldest page
    memory = []
    fault_count = 0
    hit_count = 0
    log = []
    
    for page in page_seq:
        if page in memory:
            hit_count += 1
            log.append((page, "HIT", memory.copy()))
        else:
            fault_count += 1
            if len(memory) < num_frames:
                memory.append(page)
            else:
                memory.pop(0)  # remove oldest
                memory.append(page)
            log.append((page, "FAULT", memory.copy()))
    
    return log, fault_count, hit_count

def optimal_paging(num_frames, page_seq):
    # Optimal removes page used furthest in future
    memory = []
    fault_count = 0
    hit_count = 0
    log = []
    
    for curr_idx, page in enumerate(page_seq):
        if page in memory:
            hit_count += 1
            log.append((page, "HIT", memory.copy()))
        else:
            fault_count += 1
            if len(memory) < num_frames:
                memory.append(page)
            else:
                # Find next use for each page in memory
                future_use = {}
                for mem_page in memory:
                    try:
                        future_use[mem_page] = page_seq.index(mem_page, curr_idx + 1)
                    except ValueError:
                        future_use[mem_page] = float('inf')
                
                # Remove page used furthest away
                to_remove = max(future_use, key=future_use.get)
                memory.remove(to_remove)
                memory.append(page)
            log.append((page, "FAULT", memory.copy()))
    
    return log, fault_count, hit_count

# --- DISPLAY ---

def show_cpu_results(processes, algo_name):
    print("\n" + "=" * 80)
    print(algo_name)
    print("=" * 80)
    print(f"{'PID':<8}{'Arrival':<10}{'Burst':<10}{'Completion':<12}{'Waiting':<12}{'Turnaround':<12}")
    print("-" * 80)
    
    for p in processes:
        print(f"{p.name:<8}{p.arrival_time:<10}{p.burst_time:<10}{p.completion_time:<12}{p.waiting_time:<12}{p.turnaround_time:<12}")
    
    avg_wait = sum(p.waiting_time for p in processes) / len(processes)
    avg_turn = sum(p.turnaround_time for p in processes) / len(processes)
    print("-" * 80)
    print(f"Average Waiting: {avg_wait:.2f}  |  Average Turnaround: {avg_turn:.2f}\n")

def show_paging_results(log, faults, hits, algo_name, num_frames):
    print("\n" + "=" * 80)
    print(algo_name)
    print("=" * 80)
    print(f"{'Page':<8}{'Result':<10}{'Memory':<50}")
    print("-" * 80)
    
    for page, result, mem in log:
        print(f"{page:<8}{result:<10}{str(mem):<50}")
    
    total = faults + hits
    fault_rate = (faults / total * 100) if total > 0 else 0
    success_rate = (hits / total * 100) if total > 0 else 0
    
    print("-" * 80)
    print(f"Total Pages Accessed: {total}")
    print(f"Page Faults: {faults}  |  Failure Rate: {fault_rate:.2f}%")
    print(f"Page Hits: {hits}  |  Success Rate: {success_rate:.2f}%\n")

# --- INPUT ---

def input_processes():
    procs = []
    print("\n--- ENTER PROCESSES ---")
    print("\nWhat to enter:")
    print("  Name      = Process name (like P1, P2, etc)")
    print("  Arrival   = When process starts (time)")
    print("  Burst     = How long it needs CPU (time)")
    print("  Priority  = Importance level (1=highest, optional)")
    print("\nExample: P1 0 8 1")
    print("  Name=P1, Arrives at time 0, needs 8 units, priority 1\n")
    
    cnt = 1
    print("(Type 'stop' to finish entering processes)\n")
    while True:
        line = input(f"Process {cnt}: ").strip()
        
        if line.lower() == 'stop':
            break
        
        try:
            parts = line.split()
            if len(parts) < 3:
                print("Error: Need Name Arrival Burst\n")
                continue
            
            name = parts[0]
            arr = int(parts[1])
            burst = int(parts[2])
            pri = int(parts[3]) if len(parts) > 3 else 0
            
            procs.append(Process(name, arr, burst, pri))
            print(f"Added {name}")
            print(f"Queue: {[p.name for p in procs]}\n")
            cnt += 1
        except:
            print("Error: Use numbers\n")
    
    return procs

def input_paging():
    print("\n--- ENTER PAGE DATA ---")
    print("\nWhat to enter:")
    print("  Frames = How many pages can fit in memory")
    print("  Pages  = List of pages being accessed (space-separated)")
    print("\nExample:")
    print("  Frames: 3")
    print("  Pages: 0 1 2 3 0 1 4")
    print("  (Memory has 3 slots, pages accessed in this order)\n")
    
    try:
        frames = int(input("Frames: "))
        pages = list(map(int, input("Pages: ").split()))
        print()
        return frames, pages
    except:
        print("Error: Use numbers\n")
        return None, None

# --- MENUS ---

def cpu_options():
    print("\n>>> CPU SCHEDULING")
    print("1. Shortest Job First (SJF)")
    print("2. Non-Preemptive Priority")
    print("3. Pre-emptive Priority")
    print("4. Round Robin")
    print("0. Back\n")
    return input("Select: ").strip()

def paging_options():
    print("\n>>> VIRTUAL MEMORY")
    print("1. FIFO")
    print("2. Optimal")
    print("0. Back\n")
    return input("Select: ").strip()

def cpu_simulator():
    while True:
        choice = cpu_options()
        
        if choice == '0':
            break
        
        if choice not in ['1', '2', '3', '4']:
            print("Invalid\n")
            continue
        
        procs = input_processes()
        if not procs:
            print("No processes\n")
            continue
        
        if choice == '1':
            res = sjf_scheduling(procs)
            show_cpu_results(res, "Shortest Job First (SJF)")
        elif choice == '2':
            res = non_preemptive_priority(procs)
            show_cpu_results(res, "Non-Preemptive Priority")
        elif choice == '3':
            res = preemptive_priority(procs)
            show_cpu_results(res, "Pre-emptive Priority")
        elif choice == '4':
            res = round_robin_scheduling(procs)
            show_cpu_results(res, "Round Robin")
        
        input("Press ENTER...")

def paging_simulator():
    while True:
        choice = paging_options()
        
        if choice == '0':
            break
        
        if choice not in ['1', '2']:
            print("Invalid\n")
            continue
        
        frames, pages = input_paging()
        if frames is None:
            continue
        
        if choice == '1':
            log, faults, hits = fifo_paging(frames, pages)
            show_paging_results(log, faults, hits, "FIFO Page Replacement", frames)
        elif choice == '2':
            log, faults, hits = optimal_paging(frames, pages)
            show_paging_results(log, faults, hits, "Optimal Page Replacement", frames)
        
        input("Press ENTER...")

def main():
    while True:
        print("\n" + "=" * 40)
        print(">>> OS SIMULATOR <<<".center(40))
        print("=" * 40)
        print("1. CPU Scheduling")
        print("2. Virtual Memory")
        print("3. Exit\n")
        
        choice = input("Select: ").strip()
        
        if choice == '1':
            cpu_simulator()
        elif choice == '2':
            paging_simulator()
        elif choice == '3':
            print("\nDone!\n")
            break
        else:
            print("Invalid\n")

main()
