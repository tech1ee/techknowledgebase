# Database Transactions: ACID Properties, Isolation Levels, and Distributed Coordination

Transactions form the bedrock of reliable database systems. When a bank transfer moves money between accounts, both the debit and credit must succeed or both must fail. When an e-commerce order is placed, inventory reduction and order creation must be atomic. Without transactions, database systems would be little more than fancy file systems, unable to guarantee the consistency that business operations require.

The ACID properties, formalized in the 1980s, define what it means for a transaction system to be correct. Atomicity ensures all-or-nothing execution. Consistency maintains database invariants. Isolation prevents concurrent transactions from interfering. Durability guarantees that committed changes survive failures. Understanding these properties deeply, including the implementation techniques that achieve them and the tradeoffs involved in different isolation levels, is essential for building reliable systems.

## The Essence of Transactions

A transaction is a logical unit of work that takes the database from one consistent state to another. This simple definition encapsulates profound implications. The transaction boundary defines what operations succeed or fail together. The consistent states before and after define what correctness means. The mechanism for achieving this defines much of database engine complexity.

Consider the classic example of transferring money between accounts. The operation involves reading one account's balance, checking if funds are sufficient, decrementing that balance, and incrementing another account's balance. If the system fails after the decrement but before the increment, money vanishes. If both operations are in a transaction, either both persist or neither does.

Transactions also isolate concurrent operations. If two transfers occur simultaneously, each should see a consistent view of account balances. Without isolation, one transfer might read a balance that another transfer is in the process of modifying, leading to incorrect decisions or lost updates.

The all-or-nothing and isolation properties require sophisticated mechanisms to achieve. Write-ahead logging enables atomicity and durability. Locking and multiversion concurrency control enable isolation. These mechanisms interact in complex ways that affect both correctness and performance.

## Atomicity: All or Nothing

Atomicity means that a transaction's operations all complete or none do. There is no partial execution visible to other transactions or surviving in the database after failure.

Achieving atomicity requires handling both deliberate rollback and unexpected failure. If application logic decides to abort a transaction, all its changes must be undone. If the system crashes mid-transaction, recovery must ensure uncommitted changes do not persist.

Write-ahead logging is the primary mechanism for atomicity. Before modifying any data page, the database writes a log record describing the change. If the transaction commits, a commit record is written. If the transaction aborts or the system crashes before commit, recovery reads the log and undoes uncommitted changes.

The log provides a sequential, durable record of all changes. Even if the system crashes while data pages are in inconsistent states, the log contains enough information to restore consistency. Recovery replays the log, redoing committed changes and undoing uncommitted ones.

Undo information in log records specifies how to reverse each change. For an update, the undo information includes the original value. For an insert, undo means deletion. For a delete, undo means reinsertion. The recovery process applies these undos to all changes from uncommitted transactions.

Savepoints provide partial rollback within a transaction. A savepoint marks a point to which the transaction can return, undoing subsequent changes while preserving earlier ones. This enables error handling that does not require abandoning the entire transaction.

## Durability: Surviving Failures

Durability means that once a transaction commits, its changes will survive any subsequent failure. The database guarantees that committed data is not lost due to crashes, power failures, or hardware problems.

Write-ahead logging also provides durability. The commit record must reach stable storage before commit acknowledgment returns to the client. As long as the log is durable, committed transactions can be recovered regardless of what happened to data pages.

Forcing the log to disk has performance implications. Disk writes are slow compared to memory operations. Databases use techniques to mitigate this cost. Group commit batches multiple transactions' commit records into single disk writes. Asynchronous commit allows transactions to proceed before the log is flushed, trading some durability for latency.

Checkpointing periodically writes all dirty pages to disk and records the checkpoint in the log. This limits how much log must be processed during recovery. Without checkpoints, recovery might need to replay the entire log history, potentially hours or days of operations.

Replication provides additional durability by maintaining copies on multiple machines. Synchronous replication waits for acknowledgment from replicas before committing, ensuring durability even if the primary fails. Asynchronous replication improves latency but risks losing recently committed transactions if the primary fails before replication completes.

## Consistency: Maintaining Invariants

Consistency means that transactions take the database from one valid state to another. Validity is defined by constraints: primary keys, foreign keys, check constraints, and application-defined rules.

The database enforces declared constraints automatically. A transaction that would violate a constraint is rejected. This enforcement happens at transaction commit or earlier, depending on constraint type and database configuration.

However, consistency is partially the application's responsibility. The database cannot know all application invariants. If an application requires that account balances never be negative, but this is not declared as a constraint, the application must ensure its transactions maintain this invariant.

Constraint deferral allows temporarily violating constraints within a transaction. Deferred constraints are checked only at commit time. This enables operations that would temporarily violate constraints, like swapping two values in a uniquely constrained column, as long as the final state is valid.

Triggers can enforce complex consistency rules. A trigger might check that an order total matches the sum of line items or that audit records are created for certain changes. Trigger execution is part of the transaction, maintaining atomicity with the triggering operation.

## Isolation: Concurrent Transaction Correctness

Isolation ensures that concurrent transactions do not interfere with each other. Each transaction should behave as if it were the only transaction running, even when many transactions execute simultaneously.

Perfect isolation, called serializability, means that the result of concurrent execution is equivalent to some serial execution of the same transactions. The transactions appear to execute one at a time in some order, even though they actually overlap.

Achieving serializability has performance costs. Strong isolation restricts concurrency. Transactions may need to wait for locks or abort and retry when conflicts are detected. These costs motivate weaker isolation levels that trade some isolation for better performance.

Understanding isolation anomalies helps in choosing appropriate isolation levels. Dirty reads occur when a transaction reads uncommitted changes from another transaction. Non-repeatable reads occur when a transaction reads the same row twice and gets different values because another transaction modified it between reads. Phantom reads occur when a transaction's predicate query returns different rows because another transaction inserted or deleted matching rows.

## Isolation Levels in Depth

SQL defines four standard isolation levels with increasing strictness.

Read uncommitted is the weakest level, allowing dirty reads. A transaction can see uncommitted changes from other transactions. This level is rarely appropriate because reading uncommitted data can lead to incorrect application behavior if the other transaction rolls back.

Read committed prevents dirty reads by only showing committed data. However, within a single transaction, reading the same row twice might yield different values if another transaction committed a change between reads. This non-repeatable read is allowed at this level.

Repeatable read prevents both dirty reads and non-repeatable reads. Once a transaction reads a row, reading it again yields the same value even if other transactions commit changes. However, phantom reads remain possible: new rows matching a query's predicate might appear.

Serializable prevents all anomalies. Concurrent execution is equivalent to some serial order. This is the strongest level but may have significant performance impact due to locking or conflict detection.

PostgreSQL's repeatable read is actually snapshot isolation, which provides stronger guarantees than the SQL standard's repeatable read but is not true serializability. Understanding the specific semantics of your database's isolation levels is important.

## Locking for Isolation

Locking is a traditional approach to isolation. Transactions acquire locks on data they access. Conflicting accesses must wait for locks to be released. Lock management prevents concurrent modifications that would violate isolation.

Read locks, also called shared locks, allow concurrent reads but block writes. Write locks, also called exclusive locks, block both reads and writes. A transaction holding a write lock has exclusive access until it releases the lock.

Two-phase locking is a protocol that guarantees serializability. In the growing phase, a transaction acquires locks as needed but releases none. In the shrinking phase, a transaction releases locks but acquires none. Once a transaction releases any lock, it cannot acquire more. This protocol ensures that the order in which transactions obtain their final lock defines a valid serialization order.

Strict two-phase locking holds all locks until transaction commit or abort. This simplifies recovery and prevents cascading aborts where one transaction's abort requires aborting others that read its uncommitted data.

Lock granularity affects both concurrency and overhead. Table-level locks have low overhead but allow little concurrency. Row-level locks allow high concurrency but have higher overhead in managing many locks. Most databases use row-level locking for data access with higher-level locks for schema changes.

Deadlocks occur when transactions wait for each other's locks. Transaction A holds lock X and wants lock Y. Transaction B holds lock Y and wants lock X. Neither can proceed. Databases detect deadlocks and abort one transaction to break the cycle.

## Multiversion Concurrency Control

Multiversion concurrency control, abbreviated MVCC, provides isolation without blocking readers. Rather than acquiring read locks, transactions see a snapshot of the database at their start time. Writers create new versions of rows rather than modifying existing ones. Readers see the version valid at their snapshot time.

MVCC enables significant concurrency improvements. Readers never block writers. Writers never block readers. The only blocking occurs between concurrent writers modifying the same row.

Each row version has visibility metadata indicating which transaction created it and potentially which transaction deleted it. When a transaction reads a row, it sees the version created by the most recent committed transaction that committed before the reading transaction's snapshot.

Garbage collection, often called vacuuming, removes old row versions that no transaction can see anymore. Without garbage collection, the accumulation of old versions would consume unbounded storage. The frequency and timing of garbage collection affects both storage usage and system performance.

MVCC naturally implements snapshot isolation. A transaction sees a consistent snapshot as of its start time. Changes committed after the snapshot started are invisible. This provides strong isolation without read locking.

Write skew is an anomaly possible under snapshot isolation but not serializability. Two transactions each read a value, make decisions based on it, and write different values without conflict. Their combined effect might violate an invariant that neither individually violated. Detecting and preventing write skew requires additional mechanisms.

## Optimistic Concurrency Control

Optimistic concurrency control assumes conflicts are rare and checks for them only at commit time. Transactions execute without acquiring locks, tracking their reads and writes. At commit, the database checks whether any concurrent transaction conflicted.

The validation phase occurs at commit. The database checks whether any row the transaction read was modified by a concurrent committed transaction. If so, the committing transaction aborts and may retry. If not, the transaction commits.

Optimistic approaches work well when conflicts are genuinely rare. Most transactions succeed on the first try. The overhead of lock acquisition and management is avoided. When conflicts are common, the cost of aborts and retries can exceed the cost of locking.

Some databases combine optimistic and pessimistic approaches. Reads use optimistic snapshot-based isolation. Writes acquire locks or use other mechanisms to prevent lost updates. This hybrid approach balances concurrency and conflict handling.

Serializable snapshot isolation extends snapshot isolation to detect and prevent anomalies like write skew. It tracks read-write dependencies between concurrent transactions and aborts transactions that would create non-serializable schedules. This provides serializability with MVCC's concurrency benefits.

## Distributed Transactions

Transactions spanning multiple databases or services introduce additional complexity. A single transaction might modify data in two databases. Both must commit or both must abort. Without coordination, partial failure could leave the system inconsistent.

Two-phase commit is the classic protocol for distributed transactions. In the prepare phase, the coordinator asks each participant to prepare to commit. Participants do everything needed to commit except actually committing, then respond whether they can commit. In the commit phase, if all participants prepared successfully, the coordinator tells them to commit. If any participant cannot prepare, all abort.

Two-phase commit has limitations. It blocks if the coordinator fails after prepare but before commit. Participants that prepared must wait to learn the outcome. This blocking reduces availability. Coordinator recovery is complex.

Three-phase commit adds a pre-commit phase to reduce blocking. If the coordinator fails, participants can communicate to determine the likely outcome. This reduces but does not eliminate the availability impact of coordinator failure.

In practice, distributed transactions are avoided when possible. Architectural approaches like saga patterns break distributed operations into local transactions with compensating actions for rollback. Event-driven architectures use eventual consistency rather than distributed atomicity.

## Savepoints and Nested Transactions

Savepoints allow partial rollback within a transaction. After establishing a savepoint, a transaction can later roll back to that point, undoing subsequent changes while preserving earlier ones.

Savepoints enable error handling patterns. An application might attempt an operation, catch errors, roll back to a savepoint, and try an alternative approach. Without savepoints, any error would require rolling back the entire transaction.

Nested transactions conceptually allow transactions within transactions. The inner transaction can commit or abort independently. Most databases implement nested transactions as savepoints rather than true independent transactions.

Subtransaction semantics affect isolation. In most implementations, inner and outer transactions share the same snapshot and locks. The outer transaction sees the inner transaction's changes immediately. Other concurrent transactions see the entire outer transaction's changes only when it commits.

Autonomous transactions are true independent transactions started from within another transaction. They have separate snapshots, locks, and commit/abort behavior. Autonomous transactions are useful for logging or auditing that must persist regardless of whether the outer transaction commits.

## Transaction Performance Considerations

Transaction design significantly affects database performance.

Transaction duration should be minimized. Longer transactions hold locks longer, blocking other transactions. They accumulate more undo information, increasing resource usage. They are more likely to conflict with other transactions.

Avoid user interaction within transactions. Waiting for user input while holding locks can cause severe blocking. Gather all input before beginning the transaction, then execute it quickly.

Batch operations appropriately. Too many small transactions have high per-transaction overhead. Too-large transactions hold locks for extended periods and are expensive to roll back if they fail. Find an appropriate batch size based on operation characteristics.

Lock ordering prevents deadlocks. If all transactions acquire locks in a consistent order, circular wait is impossible. Documenting and enforcing lock order requires discipline but eliminates deadlock risk.

Retry logic handles transient conflicts. Under high concurrency, some transactions will abort due to conflicts. Well-designed applications retry aborted transactions, ideally with backoff to reduce further conflict probability.

Read-only transactions can use snapshot isolation without concern for anomalies. They never write, so write-related anomalies cannot occur. Declaring transactions as read-only enables optimizations.

## Transaction Monitoring and Troubleshooting

Production transaction problems require systematic diagnosis.

Lock contention manifests as transactions waiting for locks. Monitor lock wait times and blocked transaction counts. Identify which locks are contended and which transactions hold them. Consider schema changes, indexing, or application changes to reduce contention.

Long-running transactions cause multiple problems. They hold locks longer, accumulate more undo data, and delay garbage collection in MVCC systems. Monitor transaction durations and investigate unusually long ones.

Deadlocks indicate lock ordering problems or high conflict rates. Monitor deadlock frequency. Analyze deadlocked transactions to understand access patterns. Consider application changes to improve lock ordering or reduce conflicts.

Undo space usage grows with transaction volume and duration. Long-running transactions prevent old undo records from being reclaimed. Monitor undo usage and identify transactions preventing reclamation.

Snapshot too old errors in MVCC systems occur when a transaction's snapshot becomes unavailable due to garbage collection. Long-running transactions or aggressive garbage collection settings can cause this. Balance transaction duration limits with garbage collection settings.

## Transaction Patterns for Applications

Several patterns help applications use transactions effectively.

Unit of work patterns encapsulate transaction management. The application interacts with a unit of work that tracks changes. At the end, the unit of work executes a single transaction with all accumulated changes. This ensures related changes are atomic.

Optimistic locking at the application level adds version numbers to entities. Updates include the expected version number in the where clause. If another transaction changed the entity, the update affects no rows, indicating a conflict. The application can then reload and retry.

Saga patterns decompose distributed operations into steps with compensating actions. Each step is a local transaction. If a later step fails, earlier steps' compensating actions undo their effects. This achieves eventual consistency without distributed transactions.

Command-Query Responsibility Segregation separates read and write models. Writes use transactions with strong consistency. Reads use eventually consistent read models optimized for query performance. This separates concerns and enables different consistency tradeoffs for different operations.

## Conclusion

Transactions are the mechanism by which databases provide reliability guarantees that applications depend upon. The ACID properties define what those guarantees mean. Implementation techniques from logging to locking to multiversion concurrency control achieve those properties with various performance tradeoffs.

Isolation levels offer a spectrum of choices between consistency and concurrency. Understanding the anomalies each level permits helps choose appropriately. Lower isolation levels enable higher throughput but require applications to handle potential anomalies. Higher isolation levels simplify application logic but may limit scalability.

Distributed transactions extend these concepts across multiple systems but add significant complexity and availability challenges. Modern architectures often prefer eventual consistency patterns that avoid distributed transactions while still providing adequate consistency guarantees for their requirements.

Effective transaction management requires understanding both the theory and the practical implications. The theory explains what guarantees are being provided and what anomalies are possible. The practical implications guide transaction design, isolation level selection, and troubleshooting when problems arise. Together, this understanding enables building systems that are both reliable and performant.
