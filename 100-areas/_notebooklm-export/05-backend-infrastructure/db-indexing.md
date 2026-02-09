# Database Indexing: B-Trees, Query Planning, and Performance Optimization

Database performance depends critically on efficient data retrieval. A table with millions of rows cannot be scanned entirely for every query. Indexes provide the mechanism for rapid data location, transforming linear searches into logarithmic lookups. Understanding how indexes work, which index types suit which access patterns, and how the query planner uses indexes enables developers to design databases that perform well under load.

The B-tree index dominates relational database indexing, providing excellent general-purpose performance for equality and range queries. Beyond B-trees, covering indexes, composite indexes, and specialized index types address specific needs. The query planner, that sophisticated component that chooses how to execute queries, makes decisions based on available indexes, data statistics, and query structure. Effective indexing requires understanding all these components together.

## Why Indexes Exist

Without indexes, finding a specific row requires examining every row in the table, a sequential scan. For a table with one million rows stored on disk, this means reading millions of rows, most of which are not needed. Even on fast storage, this is prohibitively slow for interactive applications.

Indexes are auxiliary data structures that enable finding rows without scanning everything. An index on customer identifier allows jumping directly to the customer's row. An index on order date allows finding orders in a date range without examining all orders.

The tradeoff is space and write overhead. Indexes consume storage, often substantially. Every insert, update, or delete must maintain all indexes on the affected table. Tables with many indexes are slower to modify. The benefit for reads must justify the cost for writes.

Choosing which columns to index is one of the most impactful performance decisions in database design. Too few indexes make queries slow. Too many indexes make writes slow and waste space. The right indexes depend on query patterns, data characteristics, and workload balance.

## B-Tree Index Structure

The B-tree, specifically the B+ tree variant used by most databases, organizes data into a balanced tree structure. Each node can have many children, determined by the branching factor. Leaf nodes contain the actual key values and pointers to table rows. Internal nodes contain keys that guide navigation to the appropriate leaf.

The height of a B-tree determines how many node accesses are needed to find any key. Because each node has many children, B-trees are shallow. A tree with a branching factor of one hundred can index ten million rows in three levels. This means any key can be found by reading at most three nodes from disk.

Keys within each node are sorted, enabling binary search within nodes. When searching for a key, the algorithm starts at the root, binary searches to find which child to descend to, and repeats until reaching a leaf. The leaf either contains the key or proves it does not exist.

Range queries benefit from B-tree structure. Leaf nodes are linked together in key order. After finding the starting point of a range, the query can follow these links to scan through the range without returning to internal nodes. This makes range queries efficient even for large ranges.

B-trees remain balanced through split and merge operations as keys are inserted and deleted. When a node becomes full, it splits into two nodes with the middle key promoted to the parent. When a node becomes too empty, it merges with a sibling. These operations keep the tree balanced without requiring full reorganization.

## Index Operations and Complexity

Understanding the complexity of index operations helps reason about performance.

Point lookups on a B-tree require traversing from root to leaf, with complexity proportional to tree height, which is logarithmic in the number of indexed values. For practical table sizes, this means a constant small number of node reads.

Range scans find the range start with a point lookup, then scan through leaf nodes covering the range. Complexity depends on how many leaf nodes the range spans. Narrow ranges are fast; ranges covering most of the table approach sequential scan performance.

Insertion finds the correct leaf node, adds the key, and potentially triggers splits up the tree. Average case is logarithmic in table size. Splits add overhead but remain bounded because the tree is balanced.

Deletion finds and removes the key, potentially triggering merges. Similar complexity to insertion with merge overhead instead of split overhead.

Updates that change indexed columns require deletion followed by insertion in the index. The row may move to a different position in the index based on its new key value. Updates to non-indexed columns do not affect the index.

## Composite Indexes

Composite indexes, also called multi-column indexes, index multiple columns together. The index is ordered by the first column, then by the second column within each first column value, and so on. This ordering has important implications for which queries can use the index.

The leftmost prefix rule determines index usability. An index on columns A, B, C can be used for queries filtering on A alone, on A and B together, or on A, B, and C together. It cannot efficiently support queries filtering only on B, only on C, or only on B and C.

This rule reflects the index's ordering. Filtering on A restricts the search to a contiguous range in the index. Within that range, filtering on B further restricts to a contiguous subrange. But filtering only on B matches values scattered throughout the index with no efficient access path.

Order of columns in a composite index matters. Put the most selective column first if all columns are used equally. Put columns used in equality conditions before columns used in range conditions. Put the column appearing in more queries first if some queries use fewer columns.

Composite indexes can also support sorting. If a query sorts by columns in index order, the index provides pre-sorted data without additional sorting. This extends to partial matches: an index on A, B, C supports sorting by A, by A then B, or by A then B then C.

## Covering Indexes

A covering index contains all columns a query needs, enabling the query to be satisfied entirely from the index without accessing the table. The query reads only index pages, avoiding the random access pattern of jumping from index entries to table rows.

When a query reads a row through an index, it first finds the row location in the index, then reads the actual row from the table. This table access is often random, with consecutive index entries pointing to widely separated table locations. For queries returning many rows, this random access dominates execution time.

A covering index includes the columns in the select list as additional index columns. The index entry contains all needed data, eliminating table access. For read-heavy queries that select specific columns, covering indexes can dramatically improve performance.

The tradeoff is index size. Including more columns makes the index larger. Larger indexes require more storage and more cache space. Updates to any included column must update the index. The benefit must justify these costs.

Many databases support included columns or index-only columns that appear in the leaf nodes but not the index key. This enables covering without affecting the index's sort order or key uniqueness.

## Index Selectivity and Statistics

Selectivity measures how well an index discriminates between rows. High selectivity means the index narrows search to few rows. Low selectivity means many rows match typical search values.

A unique index has perfect selectivity: every search finds at most one row. A boolean column has poor selectivity: typical searches match half the rows. Columns with many distinct values tend to be more selective than columns with few distinct values.

The query planner uses statistics about column value distributions to estimate selectivity. Histograms capture how values are distributed. Most common value lists identify skewed values. These statistics enable the planner to estimate how many rows match query predicates.

Statistics must be current to guide good plans. Outdated statistics can cause the planner to expect different row counts than actually result, leading to poor plan choices. Most databases automatically update statistics, but heavy write workloads may benefit from more frequent updates.

Selectivity affects whether an index is worth using. If an index search matches few rows, using it is much faster than a sequential scan. If it matches most rows, the overhead of index access may exceed the cost of simply scanning the table. The crossover point depends on many factors but is often around five to fifteen percent of table size.

## The Query Planner

The query planner, also called the query optimizer, transforms SQL queries into execution plans. It considers available indexes, statistics, join methods, and other factors to choose an efficient plan.

Query parsing converts SQL text into a parse tree representing the query structure. Optimization transforms this tree into an execution plan, choosing access methods for each table and join methods for combining tables.

Cost-based optimization estimates the cost of different plans and chooses the cheapest. Costs combine estimates for disk reads, CPU processing, memory usage, and other resources. The model is imperfect, but cost-based optimization generally produces good plans.

Rule-based optimization applies transformation rules without estimating costs. Some optimizations are always beneficial, like eliminating unnecessary sorts. Rule-based transformations simplify the plan before or after cost-based optimization.

The planner generates alternative plans and compares their costs. For simple queries, it may consider all reasonable alternatives. For complex queries, it uses heuristics to limit the search space, potentially missing optimal plans but finding good ones quickly.

## Understanding Execution Plans

Execution plans reveal how the database will or did execute a query. Learning to read plans is essential for understanding and improving query performance.

Explain output shows the planned execution before running the query. Explain analyze shows actual execution including real times and row counts. The difference reveals whether estimates matched reality.

Plan nodes form a tree with each node producing rows consumed by its parent. Leaf nodes scan tables or indexes. Interior nodes join, sort, aggregate, or transform rows. The root node produces the final result.

Scan methods include sequential scan, reading every row; index scan, using an index to find matching rows; and index only scan, reading from a covering index without table access. The planner chooses scan methods based on selectivity and available indexes.

Join methods include nested loop, hash join, and merge join. Nested loops iterate through one table and probe the other for each row, efficient when the inner side is indexed. Hash joins build a hash table on one side and probe with the other, efficient for equi-joins without indexes. Merge joins sort both sides and merge, efficient when data is already sorted or indexes provide order.

Costs in plans are estimates, not wall-clock times. Startup cost is the cost before the first row is produced. Total cost is the cost to produce all rows. Comparing costs between plan alternatives guides optimization.

## Index Selection Strategies

Choosing which indexes to create requires understanding query patterns and workload characteristics.

Analyze query logs to identify frequently executed queries and their filter and join conditions. The most impactful indexes support the most common and expensive queries. Rare queries may not justify dedicated indexes.

Primary keys automatically get indexes in most databases. Foreign keys should generally have indexes to support joins and referential integrity checks. These baseline indexes cover common access patterns.

Filter columns in where clauses are index candidates. Columns with high selectivity benefit most. Columns appearing in many queries justify index overhead. Range conditions on dates and numeric values often benefit from indexes.

Join columns typically benefit from indexes on at least one side. The planner can use indexes to make nested loop joins efficient. Without indexes, hash or merge joins are necessary.

Order by columns can use indexes to avoid sorting. This is particularly valuable for queries that use limit, where getting the first few rows in order from an index is much faster than sorting all matching rows.

Group by columns can benefit from indexes that provide sorted input, enabling streaming aggregation without accumulating all groups in memory.

## Avoiding Index Pitfalls

Several common issues reduce index effectiveness.

Using functions on indexed columns typically prevents index use. A query filtering where upper of name equals a value cannot use an index on name. The index orders by the column value, not the function result. Function-based indexes specifically index the function result but only help for that exact function.

Type mismatches can prevent index use. Comparing a string column to a numeric literal may require conversion that prevents index use. Ensuring query literal types match column types avoids this issue.

Null handling affects index use. Some databases do not include null values in indexes. Queries filtering for null cannot use such indexes. Understanding your database's null indexing behavior matters.

Like patterns starting with wildcards cannot use standard indexes. A like pattern matching anything ending with a string requires scanning the entire index or table. For suffix matching, separate indexes on reversed values or full-text indexes may help.

Inequality conditions on composite index columns stop further column use. An index on A, B, C used with A equals something and B greater than something cannot efficiently filter on C because the B range scatters matching rows.

## Partial and Conditional Indexes

Partial indexes, also called filtered indexes, index only rows matching a condition. An index on active orders includes only rows where status equals active. This produces a smaller, more efficient index for queries that match the condition.

Partial indexes are valuable when queries consistently filter on the index condition. If most queries want active records and most records are archived, a partial index on active records is much smaller and faster than an index on all records.

The query must include the index condition for the partial index to be usable. A query without the status filter cannot use a partial index filtered on status. The planner must recognize that the query's predicates imply the index's predicate.

Partial indexes reduce storage and maintenance overhead for the excluded rows. They are not updated when excluded rows are modified. This makes them particularly valuable for append-mostly tables where historical rows rarely change.

## Specialized Index Types

Beyond B-trees, databases offer specialized indexes for specific access patterns.

Hash indexes provide constant-time lookup for equality conditions. They cannot support range queries. Some databases use hash indexes automatically for specific optimizations but do not expose them for general use.

Bitmap indexes store bitmaps indicating which rows contain each value. They are efficient for low-cardinality columns and can be combined with boolean operations. They are common in analytical databases but less so in transactional systems.

Generalized inverted indexes, often called GIN indexes, support full-text search, array containment, and similar operations. They index the elements within composite values, enabling queries on array elements or text words.

Generalized search tree indexes, or GiST indexes, support spatial data, range types, and custom data types. They enable proximity searches, overlap checks, and other non-traditional queries.

BRIN indexes store summary information for ranges of physical pages. They are extremely compact but only useful when data is physically ordered by the indexed column. Time-series data naturally ordered by timestamp is a good fit.

Each specialized index type optimizes for specific access patterns at the cost of others. Understanding what patterns each type supports guides appropriate selection.

## Index Maintenance

Indexes require ongoing maintenance to remain effective.

Fragmentation accumulates as pages split and empty from modifications. Severely fragmented indexes use more space and require more reads. Rebuilding or reorganizing indexes restores efficiency.

Bloat occurs in some databases when deleted entries leave empty space that is not reclaimed. Routine maintenance reclaims this space. Monitoring bloat helps identify when maintenance is needed.

Statistics become stale as data changes. Outdated statistics cause suboptimal plans. Regular statistics updates or automatic update mechanisms keep the planner informed.

Unused indexes waste space and slow writes without benefiting reads. Monitoring index usage identifies candidates for removal. Dropping unused indexes reduces overhead with no query impact.

Index monitoring tracks usage patterns, maintenance needs, and effectiveness. Metrics like index scans versus sequential scans, estimated versus actual rows, and index size growth inform tuning decisions.

## Indexing for Specific Workloads

Different workloads require different indexing strategies.

OLTP workloads have many short transactions reading and writing small numbers of rows. Point queries on primary keys dominate. Index overhead for writes is a significant concern. Covering indexes for frequent read patterns and careful index selection balance read and write performance.

Analytical workloads have few long queries reading large data volumes. Sequential scans may be appropriate for full-table analytics. Indexes help when filtering is selective. BRIN indexes suit naturally ordered analytical data. Partial indexes for frequently analyzed subsets reduce scan scope.

Mixed workloads require balancing OLTP and analytical needs. Separate indexes may serve each pattern. Materialized views with their own indexes can accelerate analytics without slowing transactional writes.

Time-series workloads have append-heavy writes with queries on recent time ranges. Partitioning by time enables dropping old data efficiently. Indexes on recent partitions support queries while historical partitions may have minimal indexing.

## Query Tuning with Indexes

When queries perform poorly, systematic analysis identifies opportunities for index improvements.

Start with the execution plan. Identify where time is spent. Look for sequential scans on large tables, hash or merge joins that could be nested loops with indexes, and sort operations that indexes could eliminate.

Check if expected indexes exist. A missing index on a frequently filtered column is an obvious improvement opportunity.

Check if existing indexes are used. If an index exists but is not used, understand why. Selectivity too low, type mismatch, function on column, or stale statistics are common causes.

Consider composite indexes when multiple columns are filtered together. An index on each column individually may be less effective than one index on the combination.

Consider covering indexes for queries that access few columns after finding many rows. The table access overhead may dominate execution time.

Test changes on representative data. Index improvements on small datasets may not hold on production-size data. Performance testing should use realistic data volumes.

## Conclusion

Indexing is both a science and an art. The science includes understanding B-tree structure, selectivity, and query planner behavior. The art involves balancing competing concerns, anticipating workload patterns, and making judgment calls about which indexes justify their overhead.

Effective indexing requires ongoing attention. Query patterns evolve. Data volumes grow. What was optimal becomes suboptimal. Regular review of query performance, index usage, and maintenance needs keeps databases performing well.

The query planner is a sophisticated partner in this process. Understanding how it chooses plans, what information it uses, and how to read its output enables productive collaboration. The developer creates appropriate indexes; the planner uses them effectively; together they achieve efficient data access.

Mastering indexing transforms database performance from mysterious to manageable. Queries that once struggled complete quickly. Workloads that once required expensive hardware run on modest systems. This mastery comes from understanding the principles, applying them thoughtfully, and continuously learning from production experience.
