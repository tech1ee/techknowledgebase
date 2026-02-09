# Discrete Mathematics: The Foundation of Computer Science

Discrete mathematics provides the mathematical foundations that computer science builds upon. Unlike continuous mathematics with its smoothly varying quantities, discrete mathematics deals with distinct, separated values—the ones and zeros, the true and false, the countable collections that characterize digital computation. Understanding sets, relations, functions, logic, and proof techniques equips you to reason precisely about algorithms, data structures, and computational systems.

## Sets: Collections as Mathematical Objects

Sets are the most fundamental mathematical structure, and virtually all other mathematical objects can be defined in terms of them. A set is simply a collection of distinct objects called elements or members. The set containing the numbers 1, 2, and 3 is written as {1, 2, 3}. Order doesn't matter—{3, 1, 2} is the same set. Repetition doesn't matter—{1, 1, 2, 2, 3} is still just {1, 2, 3}.

Membership is the fundamental relationship with sets. Either an element is in a set or it isn't. We write "5 is an element of the set of integers" symbolically as 5 belongs to the integers. We write "0.5 is not an element of the integers" to express that fractional numbers don't belong to the whole numbers.

Sets can be described by listing elements (enumeration) or by describing a property that determines membership (set-builder notation). "The set of all positive even integers" is infinite and cannot be listed, but can be described as all numbers of the form 2n where n is a positive integer.

The empty set, containing no elements, is fundamental. It's denoted by the empty set symbol or sometimes by empty braces. Every set contains the empty set as a subset. The empty set might seem trivial, but it plays a crucial role—like zero in arithmetic.

Subset relationships describe when every element of one set is also in another. If every element of A is also in B, then A is a subset of B. The set of positive even integers is a subset of the positive integers, which is a subset of all integers, which is a subset of all rational numbers, and so on.

Set operations combine sets in various ways. The union of sets A and B contains elements that are in A, in B, or in both. The intersection contains only elements that are in both A and B. The difference A minus B contains elements of A that are not in B. The complement of A (relative to some universal set) contains elements not in A.

These operations have algebraic properties that parallel Boolean logic. Union is like "or," intersection is like "and," and complement is like "not." De Morgan's laws state that the complement of a union is the intersection of the complements, and the complement of an intersection is the union of the complements. These properties are not just abstract—they underlie how conditions combine in programming.

The power set of a set A is the set of all subsets of A, including the empty set and A itself. If A has n elements, its power set has 2^n elements. This exponential relationship appears throughout computer science—the possible states of n boolean variables, the possible subsets of n items, the possible configurations of n bits.

Cartesian products combine sets differently. The Cartesian product of A and B is the set of all ordered pairs where the first element comes from A and the second from B. Unlike sets where order doesn't matter, ordered pairs are ordered—the pair (1, 2) is different from (2, 1). Cartesian products extend to more than two sets, giving ordered tuples.

## Relations: Connections Between Elements

A relation connects elements of sets in a structured way. Formally, a relation from set A to set B is a subset of the Cartesian product of A and B—a collection of ordered pairs indicating which elements are related.

Relations pervade computer science. "Less than" is a relation on numbers: the pair (3, 5) is in the relation because 3 is less than 5. "Is a friend of" is a relation on people in a social network. "Can reach" is a relation on nodes in a graph. Database tables represent relations in the formal sense.

Relations have properties that characterize their behavior. A relation on a set A (a relation from A to A) might be:

Reflexive if every element is related to itself. Equality is reflexive—everything equals itself. "Less than" is not reflexive—no number is less than itself.

Symmetric if whenever a is related to b, b is also related to a. "Is a friend of" (in most social contexts) is symmetric. "Less than" is not symmetric—if a is less than b, then b is not less than a.

Antisymmetric if whenever a is related to b and b is related to a, then a must equal b. "Less than or equal" is antisymmetric—if a is at most b and b is at most a, then a equals b. "Less than" is also antisymmetric (vacuously—the condition never arises).

Transitive if whenever a is related to b and b is related to c, then a is related to c. "Less than" is transitive. "Is a friend of" in real life might not be—a friend of your friend isn't necessarily your friend.

An equivalence relation is reflexive, symmetric, and transitive. Equivalence relations partition a set into equivalence classes—groups of elements that are all equivalent to each other. "Has the same remainder when divided by 5" is an equivalence relation on integers, partitioning them into five classes.

A partial order is reflexive, antisymmetric, and transitive. "Less than or equal" on numbers is a partial order where every pair of elements is comparable. "Is a subset of" is a partial order on sets where not every pair is comparable—neither {1, 2} is a subset of {2, 3} nor vice versa.

Total orders are partial orders where every pair of elements is comparable. Numbers under "less than or equal" form a total order. Sets under "is a subset of" don't form a total order.

## Functions: Reliable Mappings

A function is a special relation where each input has exactly one output. While relations can connect an element to zero, one, or many others, a function must connect each element of its domain to exactly one element of its codomain.

Functions are everywhere in computing. Mathematical functions like sine or square root map numbers to numbers. Algorithms are functions mapping inputs to outputs. Hash functions map keys to indices. Programs are functions from inputs to outputs (for deterministic programs, at least).

Functions have key properties. A function is injective (one-to-one) if different inputs always give different outputs—no two inputs map to the same output. A function is surjective (onto) if every element of the codomain is hit by some input—nothing in the target is missed. A function is bijective if it's both injective and surjective—a perfect one-to-one correspondence between domain and codomain.

Bijections are particularly important because they can be inverted. If f is a bijection from A to B, there exists an inverse function from B back to A. Encryption functions should be bijective (so decryption is possible). Bijections between finite sets mean the sets have the same size (cardinality).

Function composition combines functions: if f maps A to B and g maps B to C, then the composition g after f maps A to C by first applying f, then g. Composition is associative—grouping doesn't matter—but generally not commutative—order matters.

## Propositional Logic: Reasoning with True and False

Logic provides a formal framework for reasoning. Propositional logic deals with propositions—statements that are either true or false—and how they combine.

Propositions are combined with logical connectives. Negation (NOT) inverts truth: NOT true is false, NOT false is true. Conjunction (AND) is true only when both operands are true. Disjunction (OR) is true when at least one operand is true. Implication (IF-THEN) is false only when the premise is true and the conclusion is false; otherwise it's true. Biconditional (IF AND ONLY IF) is true when both sides have the same truth value.

Implication deserves careful attention because its definition surprises many. "If P, then Q" is considered true whenever P is false, regardless of Q. This "vacuous truth" seems odd but makes logical sense: the statement only makes a claim about what happens when P is true. If P is never true, the statement cannot be violated.

Logical equivalence means two expressions have the same truth value for all combinations of their variables. De Morgan's laws, mentioned with sets, apply here: NOT (P AND Q) is equivalent to (NOT P) OR (NOT Q). The implication "if P then Q" is equivalent to "(NOT P) OR Q." These equivalences underlie logical reasoning and simplification.

Tautologies are expressions that are always true, regardless of the truth values of their variables. "P OR NOT P" (law of excluded middle) is a tautology. Contradictions are always false—"P AND NOT P" is a contradiction. Contingent expressions are sometimes true, sometimes false, depending on the values.

Logical arguments use inference rules to derive conclusions from premises. Modus ponens says: from "P implies Q" and "P," we can conclude "Q." Modus tollens says: from "P implies Q" and "NOT Q," we can conclude "NOT P." These rules are the building blocks of formal proof.

## Predicate Logic: Adding Variables and Quantifiers

Propositional logic handles combinations of fixed propositions but can't express statements about "all" or "some" elements. Predicate logic extends propositional logic with variables, predicates, and quantifiers.

A predicate is a statement with variables that becomes a proposition when values are substituted. "x is greater than 5" is a predicate; substituting x = 7 gives the true proposition "7 is greater than 5." Substituting x = 3 gives the false proposition "3 is greater than 5."

Quantifiers specify how many elements satisfy a predicate. The universal quantifier (for all) asserts that a predicate holds for every element in the domain. "For all x, x squared is non-negative" asserts that every number's square is non-negative. The existential quantifier (there exists) asserts that a predicate holds for at least one element. "There exists x such that x squared equals 2" asserts that some number's square equals 2.

Quantifier order matters when multiple quantifiers are involved. "For all x, there exists y such that y is greater than x" means that for every number, there's a bigger one—true for real numbers. "There exists y such that, for all x, y is greater than x" means there's a number bigger than all numbers—false. The quantifiers are the same; only the order changed.

Negating quantified statements swaps quantifiers: NOT (for all x, P(x)) is equivalent to (there exists x, NOT P(x)). NOT (there exists x, P(x)) is equivalent to (for all x, NOT P(x)). "Not all students passed" means "some student didn't pass." "No student passed" means "every student didn't pass."

Predicate logic is essential for precise specification. Database query languages, program specifications, mathematical definitions, and formal verification all use predicate logic to express precise conditions.

## Proof Techniques: Establishing Truth

Mathematics establishes truth through proof—rigorous arguments that derive conclusions from premises using accepted inference rules. Different proof techniques suit different situations.

Direct proof starts with hypotheses and applies rules to reach the conclusion. To prove "if n is even, then n squared is even," assume n is even (so n = 2k for some integer k), compute n squared = 4k squared = 2(2k squared), observe this is twice an integer, hence even.

Proof by contrapositive leverages the logical equivalence of "if P then Q" with "if NOT Q then NOT P." To prove "if n squared is even, then n is even," prove the contrapositive: "if n is not even (i.e., n is odd), then n squared is not even (i.e., n squared is odd)." If n is odd, n = 2k + 1, so n squared = 4k squared + 4k + 1 = 2(2k squared + 2k) + 1, which is odd.

Proof by contradiction assumes the conclusion is false and derives a contradiction. To prove the square root of 2 is irrational, assume it's rational, so the square root of 2 equals p/q for integers p and q in lowest terms. Then 2 equals p squared over q squared, so p squared equals 2 times q squared, meaning p squared is even, so p is even (from the previous proof). Let p equal 2m. Then 4m squared equals 2 times q squared, so q squared equals 2m squared, meaning q is even. But if both p and q are even, the fraction wasn't in lowest terms—contradiction. Therefore the assumption was false, and the square root of 2 is irrational.

Proof by cases divides into exhaustive possibilities and proves each. To prove something about integers, you might separately handle positive, zero, and negative cases.

Mathematical induction proves statements about natural numbers. To prove property P holds for all positive integers, prove the base case P(1), and prove the inductive step: if P(k) holds, then P(k+1) holds. The base establishes the starting point; the step establishes that truth propagates to successors; together they cover all positive integers.

Strong induction allows the inductive step to assume P holds for all values up to k when proving P(k+1). This is sometimes more convenient but is logically equivalent to regular induction.

Structural induction extends the idea to recursively defined structures. To prove a property holds for all binary trees, prove it for a single node (base case) and prove that if it holds for subtrees, it holds for a tree built from those subtrees (inductive step).

## Counting and Cardinality

How large is a set? For finite sets, we can count elements. For infinite sets, cardinality captures a notion of size based on bijections.

Two sets have the same cardinality if a bijection exists between them. Finite sets with n elements have cardinality n. But infinite sets reveal surprising truths.

The natural numbers (0, 1, 2, 3, ...) and the integers (..., -2, -1, 0, 1, 2, ...) have the same cardinality—a bijection exists (mapping 0 to 0, 1 to 1, -1 to 2, 2 to 3, -2 to 4, ...). Sets with the same cardinality as the natural numbers are called countably infinite or denumerable.

The rational numbers are also countably infinite, despite seeming "denser" than integers. A clever enumeration (listing them systematically, skipping duplicates) establishes a bijection with naturals.

But the real numbers have strictly larger cardinality. Cantor's diagonal argument shows no bijection can exist between naturals and reals: given any attempted enumeration of reals, construct a real that differs from the nth listed real in the nth decimal place—this real isn't in the list, so the enumeration is incomplete.

This proves that different sizes of infinity exist. The cardinality of naturals is called aleph-zero. The cardinality of reals is called the cardinality of the continuum. This has implications for computing—there are more real numbers than programs, so most real numbers can't be computed.

## Graph Theory Connections

While graphs deserve their own treatment, they connect deeply to discrete mathematics. A graph is a set of vertices and a set of edges (pairs of vertices). Graph concepts are defined set-theoretically.

Adjacency is a relation on vertices—vertex v is adjacent to vertex w if an edge connects them. Paths are sequences of edges connecting vertices. Reachability (can a path connect two vertices?) is the transitive closure of adjacency.

Graph properties often involve counting or logic. A graph is connected if, for all pairs of vertices, a path exists between them. A graph is bipartite if vertices can be partitioned into two sets with edges only between sets, not within.

The mathematical foundations—sets, relations, functions, logic—provide the precise language to define and reason about graphs.

## Applications Throughout Computer Science

Discrete mathematics pervades computer science.

Data structures are built on sets, relations, and functions. A set data structure implements the mathematical set operations. A map implements a function. A graph data structure implements vertex and edge sets with adjacency relations.

Database theory uses relation algebra (operations on relations in the mathematical sense) as its theoretical foundation. SQL queries implement set and relational operations.

Logic underlies programming and verification. Boolean expressions in conditionals are propositions. Loop invariants and preconditions/postconditions use predicate logic. Formal verification proves properties about programs using logical reasoning.

Algorithm analysis uses counting (how many operations?) and recurrence relations (solved by techniques including induction). Complexity theory reasons about sets of problems and their relationships.

Cryptography uses number theory (explored elsewhere) and relies on counting arguments (how many possible keys?). Security proofs are formal mathematical proofs.

Type systems in programming languages use logic—types correspond to propositions in deep ways (the Curry-Howard correspondence). Type checking verifies logical consistency.

## Thinking Precisely

Perhaps the greatest value of discrete mathematics is training in precise thinking. Mathematical definitions are exact—a function is or isn't injective, a relation is or isn't transitive. Proofs must be airtight—each step must follow from previous ones.

This precision transfers to computing. Specifications must be exact—ambiguity causes bugs. Code must be correct—almost right is wrong. Edge cases matter—the empty set, the boundary conditions.

Programming is applied discrete mathematics. Variables are like mathematical variables. Conditions are propositions. Loops implement induction (informally). Data structures implement mathematical structures. Algorithms implement mathematical functions.

Understanding the mathematical foundations doesn't just help with specific techniques—it shapes how you think about computation. When you reason about invariants, you're using logic. When you analyze algorithms, you're counting and proving. When you design data structures, you're implementing sets and relations.

Discrete mathematics is the bedrock on which computer science is built. From the basic operations on sets to the power of logical reasoning to the techniques of mathematical proof, these foundations support everything else.
