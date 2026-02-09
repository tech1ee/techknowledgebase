# Stacks, Queues, and Deques: Ordered Access Patterns

## The Philosophy of Restricted Access

Among data structures, stacks and queues occupy a special position because they intentionally limit what operations you can perform. While arrays and linked lists allow access to any element, stacks and queues provide access only to specific elements, typically those at the ends of the collection. This restriction might seem like a disadvantage, but it actually provides clarity and guarantees that enable both simpler reasoning about code and efficient implementation.

Think of these structures as enforcing a discipline on how data enters and exits. Just as a physical queue at a coffee shop ensures fairness by serving people in the order they arrived, a queue data structure enforces first-in-first-out ordering. Just as a stack of plates in a cafeteria means you take the most recently added plate, a stack data structure enforces last-in-first-out ordering. These orderings are not arbitrary constraints but rather models of how many real-world processes and computational problems naturally behave.

The power of these abstractions lies in their simplicity. When you use a stack, you know exactly which element you will access next: the one most recently added. When you use a queue, you know you will access elements in the order they were added. This predictability simplifies program design because you can reason about the order of operations without tracking individual elements. The structure itself maintains the ordering invariant, freeing you to focus on higher-level logic.

Both stacks and queues can be implemented efficiently using either arrays or linked lists, with each implementation offering constant time for all primary operations. The choice between implementations affects memory usage patterns and resizing behavior but not the fundamental operations that define these structures.

## Understanding the Stack

A stack is a collection where elements are added and removed from the same end, called the top. The last element added is the first element removed, giving rise to the term last-in-first-out, often abbreviated LIFO. Imagine a stack of books on a desk: you place new books on top, and when you need a book, you take the one on top. Retrieving a book from the middle of the stack would require removing all the books above it first.

The fundamental operations on a stack are push, which adds an element to the top, and pop, which removes and returns the element from the top. A third operation, often called peek or top, returns the top element without removing it, allowing you to examine what you would pop without actually modifying the stack. Checking whether the stack is empty rounds out the essential operations.

Every push increases the stack size by one, placing the new element above all existing elements. Every pop decreases the stack size by one, removing the most recent addition. If you push the elements one, two, three in that order, the stack contains three on top, then two below it, then one at the bottom. Popping returns three first, then two, then one. The original order is reversed, which is actually useful for many algorithms.

Stacks appear naturally whenever a process must remember where it came from to eventually return there. The classic example is function call management in programming languages. When function A calls function B, the system must remember where in A to resume after B completes. If B calls function C, the system must remember both return points. These return addresses form a stack: C's return point is on top, B's below it, and A's at the bottom. When C finishes, the system pops its return point and resumes in B. When B finishes, it pops and resumes in A. This call stack is so fundamental that it gives the stack data structure its name.

## Stack Implementation Approaches

Implementing a stack with an array means using one end of the array as the top. Maintain a variable tracking the index of the current top element. Push writes the new element at the index after the current top and increments the top index. Pop reads the element at the top index and decrements the index. Both operations take constant time because they affect only the end of the array, requiring no shifting of other elements.

When the array fills, you either reject new pushes with a stack overflow error or resize the array to create more space, depending on whether you want a fixed-capacity stack or a dynamically growing one. Resizing follows the same amortized constant time approach as dynamic arrays: allocate a larger array, copy existing elements, and continue. The occasional expensive resize averages out to constant cost per operation over time.

Implementing a stack with a linked list means treating the head of the list as the top of the stack. Push adds a new node at the head, which linked lists do in constant time. Pop removes the head node, also constant time. This implementation naturally grows and shrinks with no wasted capacity and no resizing operations, but each element incurs the overhead of a linked list node, including memory for the pointer to the next node.

The array implementation offers better memory efficiency for small elements and better cache performance for operations that examine multiple stack elements. The linked list implementation offers true constant time operations with no amortization and no capacity limits short of available memory. For most applications, either implementation works well, and the choice often follows from conventions in the programming language or framework being used.

## Real-World Stack Applications

Stacks solve problems wherever last-in-first-out ordering matches the problem structure. Recognizing these situations allows you to apply stacks effectively.

Expression evaluation and parsing rely heavily on stacks. Consider evaluating a mathematical expression with nested parentheses. As you scan from left to right, each opening parenthesis means starting a new sub-expression, and each closing parenthesis means finishing that sub-expression and incorporating its result into the enclosing expression. A stack tracks these nested levels perfectly: push when you see an opening parenthesis, pop and combine when you see a closing parenthesis. The stack naturally handles arbitrary nesting depth.

Converting expressions between different notations, like infix notation where operators appear between operands to postfix notation where operators follow operands, uses a stack to handle operator precedence. The stack holds operators waiting to be output, with lower-precedence operators unable to output until higher-precedence operators above them have been processed. Postfix notation, once created, can be evaluated with another simple stack algorithm: push numbers, and when you see an operator, pop its operands, apply the operator, and push the result.

Undo functionality in applications uses a stack of actions. Each user action pushes a record onto the stack. Undo pops the most recent action and reverses it. This naturally handles multiple levels of undo: keep popping and reversing until you reach the desired earlier state. Redo can be implemented with a second stack that receives popped actions, allowing you to reverse the reversal.

Browser back buttons work similarly. Each page visit pushes the previous page onto a history stack. Clicking back pops the most recent page and navigates there. The forward button uses a second stack that receives popped pages, enabling navigation in both directions through history.

Depth-first traversal of trees and graphs uses a stack to track which nodes to visit next. Push the starting node, then repeatedly pop a node, process it, and push its children or neighbors. The stack ensures you explore deeply into one branch before backtracking to explore others. Recursion naturally implements depth-first traversal because the call stack handles the bookkeeping, but explicit stacks allow iterative implementations when recursion would exhaust call stack limits.

## Understanding the Queue

A queue is a collection where elements are added at one end and removed from the other. The first element added is the first element removed, giving rise to the term first-in-first-out, often abbreviated FIFO. This models the fairness of a line at a store: whoever arrives first gets served first, and newcomers join at the back.

The fundamental operations on a queue are enqueue, which adds an element at the rear, and dequeue, which removes and returns the element from the front. Peeking at the front element without removing it and checking whether the queue is empty complete the essential operations.

If you enqueue the elements one, two, three in that order, one is at the front and three is at the rear. Dequeuing returns one first, then two, then three, preserving the original order. This order preservation is the essence of queue behavior and contrasts with the reversal that stacks produce.

Queues appear wherever fairness or sequencing matters. Processing requests in the order received, handling messages in the order sent, and scheduling tasks in the order requested all call for queue behavior. The structure ensures nothing gets unfairly delayed by items that arrived later.

## Queue Implementation with Arrays

Implementing a queue with an array requires more thought than a stack because both ends of the queue are active. If you enqueue at one end of the array and dequeue from the other, the used portion of the array walks along as elements are added and removed. Eventually, you might have empty space at the beginning of the array and used space at the end, with no room to enqueue even though total usage is low.

The circular array or ring buffer solves this elegantly. Instead of viewing the array as having a beginning and end, treat it as a circle where the last index wraps around to the first. Maintain two indices: front, pointing to the element that would be dequeued next, and rear, pointing to where the next enqueue would place an element. Enqueue places an element at rear and advances rear, wrapping around to zero if it passes the array end. Dequeue reads from front and advances front, also wrapping around as needed.

With circular indexing, the used portion of the array can span from some middle index, wrap around the end, and continue at the beginning. The array feels like a circle, with front and rear chasing each other around. Both enqueue and dequeue take constant time, performing only a write or read and an index increment with modular arithmetic for wrapping.

Determining whether the queue is full or empty requires care because both conditions have front and rear at the same position. Common solutions include maintaining a count of elements, wasting one array slot so that full means rear is one behind front while empty means they are equal, or using a boolean flag to distinguish the cases.

When the circular array fills, growing it requires allocating a larger array and copying elements. The copy must unwrap the circular arrangement, copying from front to the array end and then from the array beginning to rear, placing all elements contiguously in the new array. The amortized analysis parallels dynamic arrays, giving amortized constant time for enqueue.

## Queue Implementation with Linked Lists

A singly linked list with a tail pointer implements a queue naturally. The front of the queue is the head of the list, where dequeue removes nodes in constant time. The rear of the queue is the tail of the list, where enqueue adds nodes in constant time. Both operations are genuinely constant time with no amortization needed.

Dequeue reads the head's data, advances the head pointer to the next node, and returns the data. Enqueue creates a new node, makes the current tail point to it, and updates the tail pointer to the new node. Special handling is needed when the queue is empty: dequeueing should fail or return a sentinel, and enqueuing must set both head and tail to the new node since a single-element queue has the same node at both ends.

The linked list implementation trades the memory overhead of node pointers for simpler growth without resizing. Each element incurs a pointer cost regardless of queue size, while the circular array has no per-element overhead but occasionally pauses for resizing. The choice depends on memory constraints, predictability requirements, and whether the queue size is bounded or variable.

## The Double-Ended Queue or Deque

A deque, pronounced like deck, generalizes both stacks and queues by allowing insertion and removal at both ends. You can add to the front or the rear, and you can remove from the front or the rear. This flexibility subsumes both the stack, add and remove from the same end, and the queue, add at one end and remove from the other, while enabling additional patterns.

The operations on a deque typically include push front and push back for adding elements, pop front and pop back for removing elements, and peek operations for examining either end. All four primary operations should ideally run in constant time.

A doubly linked list implements a deque naturally, with constant time operations at both ends. The list's head and tail correspond to the deque's front and back. Insertion and deletion at either end follow the standard doubly linked list procedures, all constant time.

A circular array can also implement a deque by allowing both front and rear indices to move in either direction. Push front decrements front and writes there, while push back writes at rear and increments rear. Both indices wrap around the array in their respective directions. Pop front reads and increments front, while pop back decrements rear and reads. The implementation is more complex than a simple queue but maintains constant time for all operations.

Deques prove useful when you need stack-like behavior at both ends, such as implementing work-stealing schedulers where threads can push and pop from their own end of a deque while other threads steal from the opposite end. Sliding window algorithms sometimes use deques to maintain information about elements in the window, adding new elements at one end and removing old elements from the other.

## Priority Queues and Their Distinction

Before leaving the topic of queues, it is worth clarifying a common point of confusion. A priority queue is not a variant of the queue we have been discussing but rather a different abstraction entirely. While a regular queue orders elements by arrival time, a priority queue orders elements by some priority value, always providing access to the highest-priority element regardless of when it was added.

Priority queues are typically implemented using heaps, which we discuss separately. The name priority queue is somewhat misleading because the structure does not have first-in-first-out behavior; an element added later might emerge before an element added earlier if it has higher priority. Think of a hospital emergency room where patients are seen based on severity rather than arrival order. The data structure matching this behavior is called a priority queue, but its implementation and characteristics differ substantially from the queues discussed here.

Understanding this distinction prevents confusion when selecting data structures. If you need order-of-arrival fairness, use a queue. If you need access to the most important element regardless of arrival order, use a priority queue implemented as a heap.

## Practical Applications of Queues

Queues appear throughout computing wherever sequential processing and fairness matter. Operating systems use queues extensively for managing resources and scheduling work.

Print spooling uses a queue to hold documents waiting to be printed. Each print request joins the back of the queue, and the printer takes documents from the front. Users expect their documents to print in the order submitted, and the queue guarantees this fairness.

Task scheduling in operating systems maintains queues of processes or threads ready to run. When a processor becomes available, it takes the next process from the queue. Round-robin scheduling cycles through the queue repeatedly, giving each process a time slice before it returns to the back of the queue. More sophisticated schedulers may use multiple queues with different priorities, but each individual queue provides first-in-first-out behavior.

Message passing systems use queues to decouple senders from receivers. The sender enqueues a message and continues without waiting. The receiver dequeues messages when ready to process them. This queue acts as a buffer that absorbs timing differences between sending and receiving rates. Message queues enable distributed systems where components operate independently and communicate through shared queue infrastructure.

Breadth-first traversal of trees and graphs uses a queue to track which nodes to visit next. Enqueue the starting node, then repeatedly dequeue a node, process it, and enqueue its children or neighbors. The queue ensures you explore all nodes at a given depth before moving deeper, contrasting with the depth-first exploration that stacks provide.

Buffering data streams uses queues to handle rate differences between producers and consumers. If data arrives faster than it can be processed, it accumulates in the queue until processing catches up. If processing is faster than arrival, the queue drains and the processor waits. The queue smooths out temporary imbalances while maintaining order.

## Comparison of Stacks and Queues

Although stacks and queues share the characteristic of restricted access, their different orderings suit different problems. Understanding when to choose each helps you match data structure to problem.

Stacks suit problems with nested or recursive structure, where the most recently encountered item must be handled before returning to earlier items. Parsing nested structures, managing function calls, backtracking search, and undo systems all fit this pattern. The reversal property of stacks, where the output order is reversed from the input order, is either useful or irrelevant to these applications.

Queues suit problems requiring fairness or preserved ordering, where items should be handled in the order they were received. Request processing, message handling, breadth-first exploration, and buffering all fit this pattern. The preserved order of queues, where output matches input order, is essential to these applications.

When your problem does not clearly fit either pattern, consider whether reversal or preservation of order matters. If you are processing independent items and order does not matter, either structure works, and you might choose based on implementation convenience or cache efficiency. If your processing might depend on order but you are unsure how, queues are often the safer default because they preserve the original sequence.

Some problems use both stacks and queues in different phases. Topological sort, which orders tasks respecting dependency constraints, can use both: a queue for processing nodes whose dependencies are satisfied and a stack for determining the final ordering. Understanding both structures lets you recognize opportunities to combine them.

## Implementation Pitfalls and Considerations

Working with stacks and queues involves several common issues that cause bugs or performance problems.

Empty structure handling requires care. Popping an empty stack or dequeueing an empty queue is an error in most implementations. Code must check for emptiness before attempting these operations or handle the error gracefully. Forgetting this check leads to crashes or undefined behavior. Some implementations return a special sentinel value for empty structures, but this requires distinguishing the sentinel from legitimate data.

Capacity limits in array-based implementations can cause stack overflow or queue full errors if the structure does not automatically resize. Fixed-capacity implementations must document their limits and provide meaningful feedback when exceeded. Dynamically resizing implementations must implement resizing correctly, including the unwrapping logic for circular arrays.

Thread safety becomes critical when multiple threads access the same stack or queue. Concurrent push and pop operations can corrupt the structure if not properly synchronized. Thread-safe or concurrent versions of these structures use locking or lock-free algorithms to handle concurrent access correctly. Choosing between blocking when the structure is full or empty and non-blocking behavior with failure indication depends on the application's needs.

Memory management in languages without garbage collection requires correctly freeing nodes in linked list implementations. Leaking nodes exhausts memory over time. For array implementations, resizing smaller when the structure shrinks significantly can return memory to the system, though this adds complexity and potential performance unpredictability.

## Stacks, Queues, and the Broader Data Structure Landscape

Stacks and queues demonstrate that restricting a data structure's interface can be beneficial rather than limiting. By guaranteeing specific ordering behaviors, these structures simplify reasoning about code and enable optimized implementations. You trade flexibility for clarity and efficiency.

This principle extends beyond stacks and queues. Many data structures provide restricted interfaces that guarantee useful properties. Sets guarantee uniqueness. Priority queues guarantee access to the extreme element. Sorted structures guarantee ordering. Each restriction provides a property you can rely on in your algorithms.

Understanding stacks and queues prepares you for more complex structures that build on similar principles. Many graph algorithms use stacks or queues at their core. Tree traversals can be expressed using stacks for depth-first and queues for breadth-first exploration. Recognizing these patterns helps you understand and implement more sophisticated algorithms.

The choice between stacks and queues often comes down to understanding your problem's natural ordering. What must be processed first: the oldest item or the newest? The answer determines your structure. And if you need flexibility at both ends, the deque provides a generalized solution without sacrificing efficiency.

Mastery of these fundamental structures, understanding their operations, implementations, and applications, provides tools you will use throughout your programming career. Their simplicity makes them easy to implement, their efficiency makes them practical for performance-sensitive code, and their clear semantics make them easy to reason about correctly.
