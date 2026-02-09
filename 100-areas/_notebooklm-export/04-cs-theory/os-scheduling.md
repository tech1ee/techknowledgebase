# CPU Scheduling: The Art of Sharing the Processor

At the heart of every multitasking operating system lies a scheduler—the component that decides which process or thread gets to use the CPU and for how long. This decision, made thousands of times per second, profoundly impacts system responsiveness, throughput, and fairness. Understanding scheduling algorithms reveals how operating systems create the illusion that many programs run simultaneously on limited hardware, and the fundamental tradeoffs involved in sharing a precious resource.

## Why Scheduling Matters

Consider what happens when you use your computer. A web browser renders pages while a music player streams audio while a document editor waits for your keystrokes while background services sync files and check for updates. You might have dozens of processes competing for CPU time, yet the computer feels responsive—music doesn't stutter, typing feels instant, and web pages load reasonably quickly.

This experience doesn't happen by accident. The scheduler orchestrates the sharing of CPU time among competing processes, making decisions that balance multiple conflicting goals. Interactive processes need quick responses to feel snappy. Background batch jobs need eventual completion. Real-time processes need guaranteed timing. All processes deserve some fairness in allocation.

Without good scheduling, systems behave poorly. A greedy process might monopolize the CPU, starving others. Interactive applications might feel sluggish because they're waiting behind compute-intensive batch jobs. Priority inversions might cause high-priority work to wait behind low-priority work. The scheduler prevents these pathologies while maximizing useful work.

The scheduling problem is fundamentally about making predictions with incomplete information. When a process becomes ready to run, the scheduler doesn't know how long it will run before blocking, whether it's interactive or batch, or how important it is to the user. The scheduler must infer these characteristics from observed behavior and use heuristics to make good decisions.

## Process States and the Ready Queue

To understand scheduling, we must first understand when scheduling decisions occur. A process can be in several states: running (currently executing on a CPU), ready (able to run but waiting for a CPU), waiting (blocked on something like I/O), or terminated. Scheduling concerns the transition from ready to running—selecting which ready process should use the CPU next.

The collection of ready processes is typically maintained in a ready queue, though "queue" is somewhat misleading since processes aren't always served in first-come order. The ready queue's organization depends on the scheduling algorithm. It might be a simple list, a priority queue, or multiple queues with different characteristics.

Scheduling decisions occur at specific points: when a process terminates (we must choose the next one), when a process blocks on I/O (we can choose another rather than idle), when a new process is created (should it run immediately or wait?), and when an interrupt occurs (perhaps a waiting process is now ready and deserves the CPU more than the current one).

Schedulers fall into two broad categories based on whether they can take the CPU away from a running process. Non-preemptive schedulers only make decisions when a process voluntarily relinquishes the CPU (by terminating or blocking). Once a process starts running, it keeps the CPU until it stops. Preemptive schedulers can interrupt a running process and switch to another. This enables better responsiveness but introduces complexity—code might be interrupted at any point, requiring careful synchronization.

Modern general-purpose operating systems use preemptive scheduling. The potential for a process to monopolize the CPU under non-preemptive scheduling is unacceptable for interactive systems. However, within specific contexts (like some real-time systems or cooperative multitasking environments), non-preemptive scheduling still has uses.

## Scheduling Metrics and Goals

Evaluating scheduling algorithms requires defining what "good" means. Different metrics capture different aspects of performance, and optimizing one often trades off against others.

Throughput measures how many processes complete per unit time. High throughput means the system does a lot of work. Batch processing systems prioritize throughput—they want to finish as many jobs as possible.

Turnaround time measures how long from when a process arrives until it completes. Users submitting batch jobs care about turnaround time—they want their job to finish quickly.

Waiting time measures how long a process spends in the ready queue, waiting for CPU time. This strips out the actual execution time and measures scheduling overhead specifically.

Response time measures how long from when a request is made until the first response is produced. Interactive users care deeply about response time—they want the system to react quickly to their input, even if the overall operation takes longer.

CPU utilization measures what fraction of time the CPU is doing useful work (not idle). Systems administrators want high utilization—an idle CPU is a wasted resource.

Fairness measures whether CPU time is distributed appropriately among processes. Different notions of fairness exist: equal time for all processes, time proportional to priority, or time proportional to some resource entitlement.

These goals often conflict. Maximizing throughput might mean running compute-intensive batch jobs continuously, which hurts interactive response time. Minimizing average response time might starve long-running jobs. Perfect fairness might mean frequently switching between processes, reducing throughput due to context switch overhead. Scheduling algorithms embody particular tradeoffs among these goals.

## First-Come, First-Served: The Simplest Approach

The simplest scheduling algorithm is First-Come, First-Served (FCFS), also known as First-In, First-Out (FIFO). Processes are served in the order they arrive. When the current process finishes or blocks, the next process in the queue runs.

FCFS is simple to implement—just a queue with processes added at the tail and removed from the head. It's fair in a simple sense—everyone waits their turn. And it's non-preemptive, so processes can run without fear of interruption.

However, FCFS performs poorly in many scenarios due to the convoy effect. Imagine a long-running compute-intensive process (call it P1) arrives, followed by several short processes (P2, P3, P4). Under FCFS, the short processes wait behind P1, even though they could quickly complete and get out of the way. The average waiting time is high because all the short jobs wait behind the long one. It's like being stuck in a grocery checkout line behind someone with a cart full of items when you just have one thing.

FCFS is also problematic for interactive processes. If a batch job is running when the user presses a key, the keystroke handling must wait until the batch job voluntarily yields or blocks. This leads to poor interactive responsiveness.

Despite its drawbacks, FCFS appears as a component of more sophisticated schedulers. Within a priority level, processes might be scheduled FCFS. For very short scheduling intervals, simpler algorithms like FCFS might outperform complex ones because they have lower overhead.

## Shortest Job First: Optimizing Average Wait Time

If we know (or can estimate) how long each process will run, we can do better than FCFS. Shortest Job First (SJF) always runs the process with the shortest expected execution time. This provably minimizes average waiting time.

The intuition is that running short jobs first gets them out of the way quickly, so fewer processes are waiting at any moment. Compare running a 10-minute job before two 1-minute jobs (average wait: [0 + 10 + 11] / 3 = 7 minutes) versus running the 1-minute jobs first (average wait: [0 + 1 + 2] / 3 = 1 minute). The order matters enormously.

SJF comes in non-preemptive and preemptive variants. Non-preemptive SJF waits for the current process to complete before selecting the next. Preemptive SJF (called Shortest Remaining Time First or SRTF) can preempt the current process if a newly arriving process has a shorter remaining time. SRTF is optimal for minimizing average waiting time but requires preemption.

The fundamental problem with SJF is that we rarely know how long processes will run. We must estimate, and estimates can be wrong. A common approach is exponential averaging: estimate the next burst length based on recent burst lengths, giving more weight to recent history. If the previous burst was longer than predicted, we adjust our estimate upward; if shorter, we adjust downward.

SJF can also lead to starvation. A process with a long expected run time might wait forever if short processes keep arriving. This unfairness is the price of optimal average wait time. Production systems using SJF-like algorithms typically include aging mechanisms that gradually increase the priority of waiting processes, ensuring eventual service.

## Round Robin: Time Slicing for Fairness

Round Robin (RR) scheduling takes a completely different approach: instead of running each process to completion, give each process a small time slice (or quantum) and then move on to the next process. The ready queue is circular; processes cycle around getting repeated time slices until they finish.

Round Robin is inherently preemptive. When a process's quantum expires, a timer interrupt fires, and the scheduler switches to the next process. This prevents any process from monopolizing the CPU and provides good interactive responsiveness—even if the system is heavily loaded, each process gets regular CPU time.

The quantum length is a critical parameter. If the quantum is too long, Round Robin degenerates into FCFS—processes run for so long before preemption that it's effectively non-preemptive. If the quantum is too short, the system spends excessive time context switching. There's a sweet spot where the quantum is long enough to do useful work but short enough for good responsiveness.

Typical quantum lengths are 10 to 100 milliseconds. This is long enough that context switch overhead (typically a few microseconds) is a small fraction of the quantum, but short enough that interactive processes get frequent service. A 10 millisecond quantum means each process gets about 100 chances per second to run, which feels responsive to humans.

Round Robin provides fairness—each process gets an equal share of CPU time. However, it doesn't distinguish between important and unimportant processes, between interactive and batch processes, or between short and long processes. Average turnaround time can be high if all processes are similar in length (they all drag each other out) compared to SJF.

Round Robin is widely used as a foundation for more sophisticated algorithms. Even when priorities or other factors determine the order of service, time slicing ensures that no process runs indefinitely without giving others a chance.

## Priority Scheduling: Not All Processes Are Equal

In real systems, some processes are more important than others. The system process managing your disk is more important than a background update checker. An audio player needs consistent CPU time to avoid skips, while a file indexer can wait. Priority scheduling assigns each process a priority and runs the highest-priority ready process.

Priority can be assigned externally (by the system administrator, by the user, or by the process creator) or internally (computed by the scheduler based on process characteristics). Static priorities don't change over a process's lifetime; dynamic priorities are adjusted as the process runs.

Priority scheduling introduces the risk of starvation. A low-priority process might never run if higher-priority processes always exist. The solution is aging: gradually increase a process's priority the longer it waits. Eventually, even the lowest-priority process becomes high-priority enough to run. After it runs, its priority resets, and the aging starts again.

A more subtle problem is priority inversion. Suppose a high-priority process H needs a resource held by a low-priority process L. H must wait for L. But if a medium-priority process M becomes runnable, it preempts L (since M has higher priority than L). Now H is effectively waiting for M, even though H has higher priority than M. The priority scheme is inverted.

Priority inheritance is one solution: when a low-priority process holds a resource needed by a high-priority process, temporarily boost the low-priority process to the high priority. This allows L to complete its critical section quickly, uninterrupted by M, after which H can proceed. Priority inheritance is complex to implement correctly but is necessary in real-time systems where priority inversions can cause missed deadlines.

## Multi-Level Queue Scheduling

Rather than a single ready queue, many systems use multiple queues, each with different characteristics. Processes are permanently assigned to a queue based on their nature—perhaps one queue for system processes, one for interactive processes, one for batch processes.

Each queue can use its own scheduling algorithm. The system queue might use FCFS for simplicity since system processes are typically well-behaved. The interactive queue might use Round Robin for responsiveness. The batch queue might use SJF to maximize throughput.

Between queues, some higher-level scheduling is needed. Fixed priority between queues is common: always run a system process if one is ready; only run interactive processes if no system process is ready; only run batch processes if no system or interactive process is ready. Alternatively, time slicing between queues gives each queue a fraction of CPU time.

Multi-Level Feedback Queues (MLFQ) extend this by allowing processes to move between queues based on their behavior. A new process starts in a high-priority queue. If it uses its entire time slice without blocking (suggesting it's compute-intensive), it moves to a lower-priority queue with a longer time slice. If it frequently blocks before using its slice (suggesting it's interactive), it stays in or moves to a higher-priority queue.

This movement automatically adapts to process behavior without requiring advance knowledge. Interactive processes stay responsive; batch processes eventually get long time slices to make progress without constant preemption; a process that changes behavior gradually migrates to an appropriate queue.

MLFQ is the basis for schedulers in many real operating systems. The details vary—how many queues, the time slice for each, the criteria for movement, aging to prevent starvation—but the core idea of feedback-based priority adjustment is widely used.

## The Completely Fair Scheduler

Linux's Completely Fair Scheduler (CFS) takes a different philosophical approach. Rather than discrete priority levels and time slices, CFS tries to give each process a fair share of CPU time continuously. It tracks how much CPU time each process has received and always runs the process that has received the least.

The key data structure is a red-black tree keyed by "virtual runtime"—a measure of how much CPU time the process has received, weighted by priority. Processes with lower virtual runtime are on the left; higher virtual runtime on the right. The scheduler always picks the leftmost process. When a process runs, its virtual runtime increases, moving it rightward in the tree. Eventually, another process becomes the leftmost and gets to run.

This creates a flow where processes continuously trade the CPU, with each receiving their fair share over time. Higher-priority processes have their virtual runtime increase slower, so they spend more time on the left and get more CPU time. Lower-priority processes have virtual runtime increase faster.

CFS doesn't have explicit time slices in the traditional sense. Instead, it uses a concept of "targeted latency"—the time period over which all runnable processes should get one turn. If there are four runnable processes, each gets one-fourth of the targeted latency as its time on CPU before it's preempted. More processes mean shorter times per process; fewer processes mean longer times.

The fairness of CFS is mathematical, not just aspirational. Over time, processes' virtual runtimes remain close together, meaning their actual CPU time (weighted by priority) remains proportional. This prevents starvation, provides good interactivity, and handles varying loads gracefully.

## Real-Time Scheduling

General-purpose schedulers optimize for throughput, fairness, or responsiveness, but they don't provide timing guarantees. For applications that must meet deadlines—controlling machinery, processing audio/video, or managing safety-critical systems—real-time scheduling is necessary.

Real-time systems come in two forms. Hard real-time systems have absolute deadlines; missing a deadline causes system failure. A pacemaker must deliver stimuli on time; a late response is not just slow but dangerous. Soft real-time systems have deadlines that are important but not absolute. A video player should display frames on time for smooth playback; occasional missed frames degrade quality but aren't catastrophic.

Rate-Monotonic Scheduling (RMS) is a classic real-time algorithm for periodic tasks. Each task runs at a fixed frequency (rate), and priorities are assigned by rate—faster tasks get higher priority. RMS is optimal for fixed-priority scheduling: if any fixed-priority algorithm can meet all deadlines, RMS can.

Earliest Deadline First (EDF) dynamically assigns priorities based on deadlines. The task with the nearest deadline always runs. EDF is optimal in a stronger sense: if any algorithm can meet all deadlines, EDF can, and EDF can achieve higher CPU utilization than RMS while still meeting deadlines.

Real-time schedulers must do admission control—deciding whether to accept a new task. If accepting a new task would cause deadline misses, the scheduler should refuse it. This requires knowing task characteristics (execution time, period, deadline) and performing schedulability analysis to determine if all deadlines can be met.

General-purpose operating systems like Linux support soft real-time through scheduling classes. The SCHED_FIFO and SCHED_RR policies give processes higher priority than normal processes and predictable scheduling behavior. A SCHED_FIFO process runs until it blocks or a higher-priority process arrives. This isn't true hard real-time (there are no guaranteed bounds on interrupt latency or kernel preemption delays), but it's sufficient for many soft real-time needs like audio processing.

## Multiprocessor Scheduling

When a system has multiple CPUs or cores, scheduling becomes more complex. The scheduler must decide not just which process to run but also on which CPU. Additional considerations arise that don't exist in single-processor systems.

Load balancing distributes processes across CPUs so that no CPU is overloaded while others are idle. Without load balancing, work might concentrate on one CPU while others sit unused. The scheduler periodically examines CPU load and migrates processes from busy CPUs to idle ones.

However, migration has costs. When a process migrates to a different CPU, its cached data is on the old CPU's cache and must be reloaded on the new CPU. For NUMA systems, the process's memory might be on a different node, making all memory accesses slower. These migration costs must be weighed against load balancing benefits.

Processor affinity is the tendency to keep a process on the same CPU where it previously ran. Soft affinity means the scheduler prefers to keep processes on the same CPU but will migrate if needed. Hard affinity means the process is bound to specific CPUs and won't migrate.

Cache affinity is a key reason for processor affinity. A process that just ran on CPU 0 likely has its working set in CPU 0's cache. Running it again on CPU 0 benefits from that cached data. Migrating it to CPU 1 loses those cache contents, leading to cache misses and slower execution.

Simultaneous Multithreading (SMT or Hyperthreading) presents another dimension. A physical core might support two logical CPUs that share the core's execution resources. Scheduling two compute-intensive threads on the same physical core (two different logical CPUs) means they compete for resources. The scheduler might prefer placing threads on separate physical cores when possible.

## Scheduling on Modern Systems

Modern operating systems combine many of these concepts into sophisticated scheduling systems. They use multiple queue levels, dynamic priority adjustment based on behavior, special handling for real-time tasks, and awareness of multiprocessor topology.

Linux's scheduler has evolved through several generations. The current CFS for normal processes is complemented by real-time scheduling classes. The scheduler understands CPU topology (cores, hyperthreads, NUMA nodes) and makes placement decisions accordingly. Energy efficiency considerations influence scheduling on mobile devices—sometimes it's better to run slowly on a power-efficient core than quickly on a performance core.

Scheduling interacts with other system components. I/O schedulers order disk requests. Network schedulers manage packet transmission. Memory allocators interact with the CPU scheduler through the relationship between memory placement and CPU placement in NUMA systems.

Containers and virtual machines add layers. A container might have its own CPU budget enforced by cgroups, limiting how much CPU time processes in the container can consume. A virtual machine has its own scheduler, which runs on virtual CPUs that are themselves scheduled by the hypervisor.

The complexity continues to grow. Heterogeneous processors (like ARM's big.LITTLE with different core types) require schedulers that understand which tasks benefit from which core types. Energy-aware scheduling trades performance for power savings. Quality-of-service guarantees for cloud workloads require schedulers that respect resource reservations.

## Scheduler Implementation Considerations

Implementing a scheduler efficiently is challenging because scheduling decisions are extremely frequent. Every time a process blocks or a timer fires, the scheduler runs. Scheduler overhead directly reduces the time available for useful work.

Data structure choices matter. A simple linked list ready queue has O(n) complexity for insertion and O(1) for removal of the head, but finding the minimum (for SJF) is O(n). Priority queues (heaps) offer O(log n) insertion and removal. CFS's red-black tree offers O(log n) for all operations and easy identification of the minimum.

Locking is critical in multiprocessor schedulers. Multiple CPUs might try to access the ready queue simultaneously. Coarse-grained locking (one lock for the entire scheduler) is simple but becomes a bottleneck. Fine-grained locking (per-CPU run queues) improves scalability but complicates load balancing.

Many schedulers use per-CPU run queues. Each CPU has its own queue of processes with affinity for that CPU. Scheduling decisions usually involve only the local queue, avoiding contention. Load balancing periodically moves processes between queues but happens less frequently than scheduling decisions.

The timer interrupt frequency affects scheduling granularity. Traditional systems used 100 Hz timers (10 ms ticks), allowing 10 ms minimum time slices. Modern systems often use 1000 Hz (1 ms) or tickless designs where timers are set dynamically based on when the next event should occur, reducing overhead when the system is idle.

## Looking at Scheduling Holistically

Scheduling is not just about algorithms but about the entire system design. Good performance requires alignment between application expectations, operating system policies, and hardware capabilities.

Applications can cooperate with the scheduler. A process that knows it won't need the CPU for a while can sleep, explicitly relinquishing the CPU. A process that knows it's about to do a long computation can lower its own priority. Applications can use real-time scheduling classes when they have timing requirements.

System administrators configure scheduling policies. Priority ranges, time slices, and queue structures are often tunable. Real-time applications might need special configuration to achieve their timing goals.

Hardware design influences scheduling. More cores change the optimal scheduling strategies. Cache sizes and topologies affect the cost of migration. Power management states interact with scheduling decisions.

The scheduler is ultimately a policy mechanism, encoding decisions about how to share a scarce resource. Different goals lead to different schedulers. A throughput-oriented batch system, a responsive desktop, a real-time embedded system, and a multi-tenant cloud server all want different things from their schedulers. Understanding scheduling means understanding these goals and the tradeoffs in achieving them.

The next time you use a computer and it feels responsive even with many programs running, appreciate the scheduler working behind the scenes. Thousands of times per second, it's making decisions about who runs next, balancing competing demands, predicting behavior, and creating the illusion that many processes run simultaneously on limited hardware. This invisible orchestration is what makes modern multitasking possible.
