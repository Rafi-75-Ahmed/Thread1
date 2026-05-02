import os
import time
import sys

# ANSI Escape Sequences
RED = "\033[91m●\033[0m"
BLUE = "\033[94m●\033[0m"
BOLD = "\033[1m"
RESET = "\033[0m"
CLEAR_LINE = "\033[K"
MSG_RED = "\033[91m"

class Resource:
    def __init__(self, name):
        self.name = name
        self.owner = None

    def acquire(self, thread_name):
        if self.owner is None or self.owner == thread_name:
            self.owner = thread_name
            return True
        return False

class ShapeThread:
    def __init__(self, name, inputs, start_x, start_y, shape_type, total_burst):
        self.name = name
        self.balls = []
        self.start_x = start_x
        self.start_y = start_y
        self.shape_type = shape_type
        self.op_cycle = ["MULTIPLY", "ADD", "RELAX"]
        self.current_op_idx = 0
        self.remaining_burst = total_burst
        self.is_finished = False
        
        for val in inputs:
            color = BLUE if int(val) % 2 == 0 else RED
            self.balls.append({'color': color, 'curr_x': 0, 'curr_y': 0})
        self.reset_to_shape()

    def reset_to_shape(self):
        if self.shape_type == "triangle": offsets = [(2, 0), (0, 2), (4, 2)]
        elif self.shape_type == "square": offsets = [(0, 0), (4, 0), (0, 2), (4, 2)]
        else: offsets = [(2, 0), (0, 2), (4, 2), (1, 4), (3, 4)]
        for i, ball in enumerate(self.balls):
            ball['curr_x'] = self.start_x + offsets[i][0]
            ball['curr_y'] = self.start_y + offsets[i][1]

    def transform(self, op):
        if op == "RELAX": self.reset_to_shape()
        for i, ball in enumerate(self.balls):
            if op == "ADD":
                ball['curr_x'], ball['curr_y'] = self.start_x + (i * 2), self.start_y + 2
            elif op == "MULTIPLY":
                ball['curr_x'], ball['curr_y'] = self.start_x + 2, self.start_y + i

def gotoxy(x, y):
    sys.stdout.write(f"\033[{y};{x}H")
    sys.stdout.flush()

def clear_area(t):
    for y in range(t.start_y, t.start_y + 7):
        gotoxy(t.start_x - 1, y); print(" " * 15)

def draw_thread(t):
    for ball in t.balls:
        gotoxy(ball['curr_x'], ball['curr_y']); print(ball['color'], end="")

def main():
    # Setup
    s1 = input("Set 1 (3 nums): ").split()
    b1 = int(input("Set 1 Burst: "))
    s2 = input("Set 2 (4 nums): ").split()
    b2 = int(input("Set 2 Burst: "))
    s3 = input("Set 3 (5 nums): ").split()
    b3 = int(input("Set 3 Burst: "))
    op_delay = float(input("Manual Step Delay (sec): "))
    quantum = int(input("Time Quantum: "))

    threads = [
        ShapeThread("Set 1", s1, 5, 8, "triangle", b1),
        ShapeThread("Set 2", s2, 35, 8, "square", b2),
        ShapeThread("Set 3", s3, 65, 8, "pentagon", b3)
    ]
    
    # Initialize Staggered Sequence
    threads[1].current_op_idx = 2 # Set 2 starts Relax
    threads[2].current_op_idx = 1 # Set 3 starts Add

    # Resource Definitions for Deadlock Simulation
    res_horiz = Resource("Horizontal_Bus")
    res_vert = Resource("Vertical_Bus")

    os.system('cls' if os.name == 'nt' else 'clear')
    for x in [30, 60, 90]: 
        for y in range(5, 22): gotoxy(x, y); print("|")
    gotoxy(92, 5); print(f"{BOLD}ACTIVITY LOG{RESET}")

    log_y = 6
    while any(not t.is_finished for t in threads):
        for t in threads:
            if t.is_finished: continue
            
            current_op = t.op_cycle[t.current_op_idx % 3]
            
            # RESOURCE ACQUISITION (The Deadlock Logic)
            needed_res = None
            if current_op == "ADD": needed_res = res_horiz
            elif current_op == "MULTIPLY": needed_res = res_vert

            if needed_res and not needed_res.acquire(t.name):
                # If resource is held by someone else, we are BLOCKED
                gotoxy(1, 2); print(f"{CLEAR_LINE}{MSG_RED}BLOCKED: {t.name} waiting for {needed_res.name}{RESET}")
                gotoxy(92, log_y); print(f"{MSG_RED}{t.name}: DEADLOCK{RESET}")
                log_y = 6 if log_y > 20 else log_y + 1
                time.sleep(2)
                continue # Skip this thread's turn

            # Execute turn
            steps = min(quantum, t.remaining_burst)
            for _ in range(steps):
                gotoxy(1, 2); print(f"{CLEAR_LINE}{BOLD}RUNNING:{RESET} {t.name} | {current_op}")
                gotoxy(92, log_y); print(f"{CLEAR_LINE}{t.name}: {current_op}...")
                time.sleep(op_delay)
                log_y = 6 if log_y > 20 else log_y + 1
                clear_area(t); t.transform(current_op); draw_thread(t)
                t.remaining_burst -= 1

            if t.remaining_burst <= 0:
                t.is_finished = True
                if needed_res: needed_res.owner = None # Release resource on finish
            else:
                t.current_op_idx += 1
                # To simulate a bug/deadlock, we DON'T release the resource here 
                # unless you want to "Fix" the deadlock.
                time.sleep(0.5); clear_area(t); t.reset_to_shape(); draw_thread(t)

    gotoxy(1, 23); print("Simulation ended.")

if __name__ == "__main__":
    main()