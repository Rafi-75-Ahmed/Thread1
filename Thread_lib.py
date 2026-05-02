import os
import time
import sys

# ANSI Escape Sequences
RED = "\033[91m●\033[0m"
BLUE = "\033[94m●\033[0m"
BOLD = "\033[1m"
RESET = "\033[0m"
CLEAR_LINE = "\033[K"

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
        
        # Color logic based on odd/even inputs
        for val in inputs:
            color = BLUE if int(val) % 2 == 0 else RED
            self.balls.append({'color': color, 'curr_x': 0, 'curr_y': 0})
        
        self.reset_to_shape()

    def reset_to_shape(self):
        """Places balls in their base geometric forms (Notebook Reference)"""
        if self.shape_type == "triangle":   # Set 1
            offsets = [(2, 0), (0, 2), (4, 2)]
        elif self.shape_type == "square":   # Set 2
            offsets = [(0, 0), (4, 0), (0, 2), (4, 2)]
        else: # pentagon (Set 3)
            offsets = [(2, 0), (0, 2), (4, 2), (1, 4), (3, 4)]

        for i, ball in enumerate(self.balls):
            ball['curr_x'] = self.start_x + offsets[i][0]
            ball['curr_y'] = self.start_y + offsets[i][1]

    def transform(self, op):
        """Moves balls based on the current operation type"""
        if op == "RELAX":
            self.reset_to_shape()
            return

        for i, ball in enumerate(self.balls):
            if op == "ADD": 
                ball['curr_x'] = self.start_x + (i * 2)
                ball['curr_y'] = self.start_y + 2
            elif op == "MULTIPLY": 
                ball['curr_x'] = self.start_x + 2
                ball['curr_y'] = self.start_y + i

def gotoxy(x, y):
    sys.stdout.write(f"\033[{y};{x}H")
    sys.stdout.flush()

def clear_area(t):
    
    for y in range(t.start_y, t.start_y + 7):
        gotoxy(t.start_x - 1, y)
        print(" " * 15)

def draw_thread(t):
    for ball in t.balls:
        gotoxy(ball['curr_x'], ball['curr_y'])
        print(ball['color'], end="")

def main():
   
    
    s1 = input("Set 1 Inputs (3 nums): ").split()
    b1 = int(input("Set 1 Manual Burst: "))
    
    s2 = input("Set 2 Inputs (4 nums): ").split()
    b2 = int(input("Set 2 Manual Burst: "))
    
    s3 = input("Set 3 Inputs (5 nums): ").split()
    b3 = int(input("Set 3 Manual Burst: "))
    
    op_delay = float(input("Enter Manual Timer Delay (sec per step): "))
    switch_delay = float(input("Enter Context Switch Delay (sec): "))
    quantum = int(input("Enter Time Quantum: "))

    # Initialization
    threads = [
        ShapeThread("Set 1", s1, 5, 8, "triangle", b1),
        ShapeThread("Set 2", s2, 35, 8, "square", b2),
        ShapeThread("Set 3", s3, 65, 8, "pentagon", b3)
    ]

    # Staggering the start according to your logic:
    # Set 1: Multiply (0) | Set 2: Relax (2) | Set 3: Add (1)
    threads[1].current_op_idx = 2 
    threads[2].current_op_idx = 1

    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Static UI Borders
    for x in [30, 60, 90]:
        for y in range(5, 22):
            gotoxy(x, y); print("|")
    gotoxy(92, 5); print(f"{BOLD}ACTIVITY LOG{RESET}")

    log_y = 6
    while any(not t.is_finished for t in threads):
        for t in threads:
            if t.is_finished: continue

            current_op = t.op_cycle[t.current_op_idx % 3]
            # Determine how many steps to run in this turn
            steps_this_turn = min(quantum, t.remaining_burst)

            for _ in range(steps_this_turn):
                # Update Status Line
                gotoxy(1, 2)
                print(f"{CLEAR_LINE}{BOLD}ACTIVE:{RESET} {t.name} | {current_op} | Burst Left: {t.remaining_burst}")
                
                # Log step and apply Manual Timer
                gotoxy(92, log_y)
                print(f"{CLEAR_LINE}{t.name}: {current_op} Step...")
                time.sleep(op_delay) 
                
                # Update Log Position
                log_y = 6 if log_y > 20 else log_y + 1

                # Animation logic
                clear_area(t)
                t.transform(current_op)
                draw_thread(t)
                t.remaining_burst -= 1

            # Round Robin Context Switch Logic
            if t.remaining_burst <= 0:
                t.is_finished = True
                gotoxy(92, log_y); print(f"{t.name} FINISHED")
                log_y = 6 if log_y > 20 else log_y + 1
            else:
                # Rotate to next operation for the next time this thread is called
                t.current_op_idx += 1
                
                # Pause for the Context Switch
                gotoxy(1, 2)
                print(f"{CLEAR_LINE}{BOLD}SWITCHING...{RESET} Next Set in {switch_delay}s")
                time.sleep(switch_delay)
                
                # Reset to base shape during the switch
                clear_area(t)
                t.reset_to_shape()
                draw_thread(t)

    gotoxy(1, 23)
    print(f"\n{BOLD}{'='*75}{RESET}")
    print(f"{'Group':<10} | {'Shape':<12} | {'Operations':<18} | {'Status':<12}")
    print("-" * 75)
    print(f"{'Set 1':<10} | {'Triangle':<12} | {'All Cycles':<18} | {'Completed':<12}")
    print(f"{'Set 2':<10} | {'Square':<12} | {'All Cycles':<18} | {'Completed':<12}")
    print(f"{'Set 3':<10} | {'Pentagon':<12} | {'All Cycles':<18} | {'Completed':<12}")
    print(f"{BOLD}{'='*75}{RESET}\n")

if __name__ == "__main__":
    main()