# System Design Case Studies: Learning from Real-World Architectures

The best way to develop system design intuition is to work through concrete problems, understanding not just what solutions look like but why specific choices make sense given particular constraints. This document presents four case studies that cover different domains and challenges: a social media timeline, a photo sharing platform, a ride-matching system, and a URL shortening service. For each, we explore the problem space, examine key design decisions, and discuss the tradeoffs involved.

## Case Study One: Designing a Twitter-Like Timeline

The timeline is the heart of a social media platform. Users follow other users, and when those followed users post content, it appears in their followers' timelines. This seemingly simple description hides enormous complexity. The scale is staggering: hundreds of millions of users, billions of relationships, and millisecond latency requirements for a satisfying user experience.

### Understanding the Problem

Before diving into solutions, we must understand what we are building. A timeline system must handle several distinct operations: creating new posts, determining which posts appear in a user's timeline, and rendering timelines quickly enough that the user experience feels instant.

The creation of posts is relatively straightforward. A user submits content, and the system stores it. The challenge lies in what happens next. When should this post appear in followers' timelines? Immediately? Eventually? And how do we ensure that users with millions of followers do not overwhelm the system when they post?

Reading timelines is the more challenging operation, primarily because of scale. If a user follows thousands of accounts, their timeline potentially draws from thousands of sources. Naively querying all these sources for every timeline request would be impossibly slow.

The access patterns are highly uneven. Some users have millions of followers, while most have few. Some users check their timeline constantly, while others visit rarely. Some posts receive enormous engagement, while most receive little. Any design must handle these variations gracefully.

### The Pull Model

The most intuitive approach to building a timeline is the pull model, also called fan-out on read. When a user requests their timeline, the system queries the posts from all accounts they follow, merges them, sorts them by time, and returns the result.

This approach has appealing simplicity. Posts are stored once when created. There is no additional work when someone posts; the work happens when timelines are read. Storage is efficient because each post exists only once rather than being copied to many timelines.

The problem with pull becomes apparent at scale. A user following a thousand accounts requires a thousand database queries, or at least a complex query with a thousand conditions. These queries must be executed, results merged and sorted, all before the user sees their timeline. The latency is unacceptable for the immediate response users expect.

Caching can help but introduces its own challenges. Caching the merged timeline means that new posts do not appear until the cache is invalidated or expires. Caching individual user's posts helps somewhat but still requires fetching and merging from many caches.

The pull model can work for small-scale systems or as part of a hybrid approach. It is not suitable as the primary mechanism for a system at Twitter's scale.

### The Push Model

The alternative is the push model, also called fan-out on write. When a user posts, the system immediately writes that post to the timelines of all their followers. Each user's timeline is a precomputed list that can be returned directly on read.

Reading becomes trivially fast. A user's timeline is a single list that can be fetched in one query. There is no merging, no sorting, no complex computation at read time. The timeline is ready and waiting.

The cost has moved from read time to write time. When a user posts, the system must update potentially millions of timelines. This fan-out operation is inherently expensive, but it can be done asynchronously. The user sees their post published immediately while the system works in the background to propagate it to followers.

Storage requirements increase dramatically with push. Instead of storing each post once, you store a reference to it in every follower's timeline. With an average of hundreds of followers per user and millions of users, this multiplication is significant. However, storage is relatively cheap, and the trade of storage for latency is often worthwhile.

The celebrity problem complicates push. When a user with ten million followers posts, the system must update ten million timelines. Even with highly optimized writes, this takes time. During that time, some followers see the post while others do not, which can be socially awkward for viral content that people expect to see simultaneously.

### Hybrid Approaches

Real systems use hybrid approaches that combine push and pull based on the characteristics of each user. The insight is that most users have few followers, so push is cheap for them. Only celebrities with massive followings create expensive fan-out operations.

In a hybrid system, posts from regular users are pushed to follower timelines immediately. Posts from celebrities, defined by some follower threshold, are not pushed. Instead, when rendering a timeline, the system fetches the precomputed timeline, which contains posts from regular users, and merges it with recent posts from celebrities the user follows.

This hybrid approach gives fast reads for the common case while limiting the write amplification caused by celebrity posts. The number of celebrities is small, so the per-timeline query cost is manageable. The merged result feels instantaneous to users.

The threshold for celebrity treatment is a tuning parameter. Too low, and too many users have their posts pulled, degrading read performance. Too high, and expensive fan-outs from high-follower users overwhelm write capacity. The right threshold depends on the specific traffic patterns of your platform.

### Timeline Ranking and Filtering

Early timeline systems showed posts in strict chronological order. Modern systems use algorithmic ranking that considers relevance, engagement probability, and other signals. This ranking is computationally expensive and adds complexity to the architecture.

Ranking cannot be precomputed entirely because it depends on the specific user viewing the timeline. Signals like previous engagement with an author, time since last visit, and context of the request all affect ranking. Some ranking must happen at read time, adding latency that the push model was designed to avoid.

Systems balance precomputation and real-time ranking. Some signals can be computed when posts are created and stored with them. Others require per-request computation. Machine learning models that score posts might run on dedicated inference infrastructure. The architecture must support all these components while maintaining acceptable latency.

Filtering adds another dimension. Users might mute certain accounts, block certain terms, or prefer not to see certain content types. These preferences must be applied when rendering timelines, either by filtering the precomputed timeline or by incorporating preferences into the ranking model.

### Storage and Retrieval

The storage layer for a timeline system must handle tremendous write volume, large data sizes, and strict latency requirements. Different parts of the system have different storage needs.

Posts themselves are relatively small and relatively static. Once created, they rarely change, though they might be deleted. A combination of a traditional database for durability and a caching layer for performance works well. Posts are accessed by ID, so simple key-value access patterns are sufficient.

Timeline data, the lists of post references for each user, requires different treatment. These lists are constantly updated as new posts arrive. They must support efficient prepending, since new posts go at the top, and efficient range queries for pagination. Some systems use specialized data structures or storage systems optimized for these access patterns.

User relationships, who follows whom, might be stored in a graph database or a specialized social graph service. This data is queried both for fan-out operations and for rendering follower and following lists. The access patterns are different enough from timeline data that separate storage often makes sense.

### Dealing with Spikes

Social media traffic is highly variable. Breaking news, major events, and viral content cause sudden spikes that can be orders of magnitude above baseline. The architecture must handle these spikes without degrading performance.

Auto-scaling can add capacity in response to increased load, but scaling takes time. By the time new capacity is provisioned, the spike might be over. More important is designing the system to degrade gracefully under load rather than collapsing.

Rate limiting protects the system from being overwhelmed. If fan-out queues grow too large, the system might slow down or temporarily switch to pull mode for some users. If read traffic exceeds capacity, the system might serve slightly stale timelines from cache rather than failing entirely.

Geographic distribution helps handle global events. Users in different regions can be served by regional infrastructure, spreading the load. Content can be replicated across regions with eventual consistency acceptable for most social media use cases.

## Case Study Two: Designing an Instagram-Like Photo Sharing Platform

Photo sharing presents different challenges from text-based social media. The primary challenge is handling media: large binary files that must be stored, processed, and delivered efficiently. The scale is immense, with billions of photos requiring petabytes of storage and enormous bandwidth for delivery.

### Understanding the Problem

Users upload photos, apply filters, add captions, and share them. Other users view these photos in feeds, on profile pages, and through direct sharing. Users engage through likes, comments, and reshares. The system must handle all of these operations at massive scale.

The core challenges are storage, processing, and delivery of media. Unlike text, photos are large, ranging from hundreds of kilobytes to several megabytes. Processing photos requires significant computation for filtering, resizing, and format conversion. Delivering photos requires substantial bandwidth.

Reliability requirements are high. Users are deeply attached to their photos, and losing them would be catastrophic. The system must provide durability guarantees that exceed typical application requirements.

### Upload and Processing Pipeline

When a user uploads a photo, several things must happen. The original file must be stored durably. Multiple sizes must be generated for different display contexts. The configured filter must be applied. Metadata must be extracted and indexed.

This processing is too slow to happen synchronously during the upload request. Users would wait uncomfortably long for their photos to post. Instead, uploads trigger asynchronous processing pipelines.

The upload itself writes the original photo to durable storage and returns immediately. A message is queued for the processing pipeline. Workers pick up these messages and perform the necessary operations: resizing, filtering, format optimization. When processing completes, the various versions are available for viewing.

The time between upload and availability is typically seconds, fast enough that users do not notice the gap. If processing fails, it can be retried without losing the original photo. The decoupling of upload and processing provides both better user experience and better reliability.

### Storage Architecture

Photo storage operates at a scale that requires specialized approaches. Billions of photos, with multiple sizes each, total to petabytes of data. Traditional file systems and databases are not designed for this scale.

Object storage systems, whether custom-built or cloud-based, are the foundation of photo storage. Object storage provides simple key-value access to arbitrarily large binary objects. It is designed to scale horizontally to any capacity, adding nodes to increase both storage and throughput.

Photos are typically stored with some form of content-addressing or structured naming. A photo might be stored with a key derived from its hash, ensuring that identical photos are not duplicated. Alternatively, keys might incorporate the user ID and photo ID, enabling sharding based on user.

Tiered storage manages costs by placing frequently accessed photos on faster, more expensive storage while moving older, less-accessed photos to cheaper archival storage. A photo from years ago, rarely viewed, does not need the same performance as a photo uploaded minutes ago that is being viewed by many followers.

Replication ensures durability. Photos are stored redundantly, typically across multiple data centers. Even if an entire data center fails, photos remain safe in other locations. The replication factor and geographic spread reflect the durability requirements and cost constraints.

### Content Delivery

Delivering photos efficiently is as important as storing them. Users expect photos to load instantly, which requires getting the data as close to them as possible.

Content delivery networks are essential for photo delivery. CDNs cache photos at edge locations around the world. When a user requests a photo, the request goes to a nearby edge server. If the edge server has the photo cached, it returns it immediately. Otherwise, it fetches from origin, caches, and returns.

The cache hit ratio determines CDN effectiveness. Popular photos viewed by many users will be cached at many edge locations. Rarely viewed photos might only exist at origin. Optimizing the cache hit ratio involves understanding access patterns, choosing appropriate cache TTLs, and sometimes prefetching content likely to be accessed.

Different photo sizes serve different purposes. Thumbnails are small, loading quickly for feeds and galleries. Full-size photos are large, used for detailed viewing. The CDN caches each size separately, optimizing for the specific access patterns of each.

Image optimization can reduce file sizes significantly without visible quality loss. Modern image formats like WebP and AVIF provide better compression than JPEG. Adaptive quality can serve lower quality to users on slow connections. These optimizations reduce bandwidth costs and improve load times.

### The Feed

Like the Twitter timeline, the Instagram feed requires aggregating content from followed users. Many of the same considerations apply: pull versus push, celebrity handling, ranking algorithms.

Photo feeds have some differences from text feeds. Photos are larger, so caching feed content is more expensive. The visual nature makes ranking particularly important; users have limited patience for scrolling through uninteresting photos. Engagement patterns differ, with likes and comments being more significant signals.

The feed architecture typically uses push for most users with pull for high-follower accounts, similar to Twitter. The feed service maintains precomputed feed lists with references to photos rather than the photos themselves. Ranking happens at request time, incorporating signals about the specific user and context.

Infinite scroll creates interesting technical challenges. Users expect to scroll indefinitely through their feed, loading more content as they go. Each page of content must be consistent with previous pages, even as new content is posted. Cursors or offsets mark the user's position, enabling stateless pagination.

### Discovery and Search

Beyond the feed of followed accounts, users discover content through explore features, hashtag browsing, and search. These features require different infrastructure than the feed.

The explore feature surfaces popular and relevant content to users. It might use collaborative filtering, showing content liked by similar users. It might use content-based recommendations, showing content similar to what the user has engaged with. These recommendation systems require substantial machine learning infrastructure.

Hashtags create an indexing challenge. Posts tagged with popular hashtags must be findable, but the volume for some hashtags is enormous. Indexes are sharded by hashtag and time, enabling efficient queries for recent posts with a given hashtag.

Visual search, finding photos similar to a given image, requires computer vision capabilities. Photos must be processed to extract feature vectors that enable similarity comparison. These vectors are indexed in specialized databases that support nearest-neighbor queries.

### Handling Scale

The photo platform faces some of the most extreme scale challenges in technology. The combination of user count, engagement level, and media size creates enormous resource requirements.

Sharding is essential at every layer. User data is sharded, often by user ID. Photo storage is sharded, often by photo ID or content hash. Indexes are sharded by various keys depending on access patterns. Effective sharding ensures that load is distributed and that no single node becomes a bottleneck.

Caching is pervasive. Metadata is cached to avoid database queries. Processed images are cached to avoid repeated processing. CDNs cache delivered content. In-memory caches store hot data for lowest latency access. Multiple layers of caching work together.

Automation is essential for operating at scale. Millions of servers cannot be managed manually. Automated deployment, automated scaling, automated failure detection and recovery enable human operators to manage vast infrastructure.

## Case Study Three: Designing an Uber-Like Ride Matching System

Ride-hailing platforms connect riders with drivers in real time. The core challenge is matching: finding an available driver near a rider who has requested a ride, quickly enough that both have a good experience. This real-time matching at scale requires sophisticated systems.

### Understanding the Problem

A rider opens the app and requests a ride from their current location to a destination. The system finds a nearby available driver, sends them the request, and if they accept, facilitates the ride. After the ride, payment is processed and ratings are collected.

The matching problem is deceptively complex. It is not just finding the nearest driver but finding the best match considering multiple factors: current location, direction they are heading, driver preferences, rider preferences, estimated arrival time, and more. And this matching must happen in seconds while drivers are continuously moving.

The real-time nature creates unique challenges. Unlike other systems where slight staleness is acceptable, ride-matching needs current information. A driver's location from ten seconds ago is already outdated. A driver who was available might have accepted another ride.

Geographic variation in supply and demand creates challenges. Some areas have many drivers and few riders, others the reverse. Surge pricing attempts to balance supply and demand economically, but the system must still function when imbalance exists.

### Location Tracking

Drivers continuously send their location to the system. This creates an enormous stream of data, millions of location updates per minute in a large market. The system must ingest these updates, store recent locations efficiently, and enable queries for drivers near a given point.

Location data is inherently geospatial and benefits from specialized indexing. Quadtrees, geohashes, and other spatial indexing techniques enable efficient queries for entities within a region. These indexes must be updated continuously as locations change.

The system must handle unreliable location data. GPS has inherent inaccuracy, especially in urban canyons with tall buildings. Devices sometimes report stale locations. Network delays mean the reported location is always slightly in the past. The matching system must account for these limitations.

Battery and data usage constrain how frequently drivers can report location. More frequent updates provide better accuracy but drain batteries faster. The reporting frequency might vary based on context, more frequent when a driver is online and available, less frequent when offline.

### The Matching Algorithm

When a ride request arrives, the system must quickly find suitable drivers and select the best match. This happens in real time with tight latency constraints.

The first step is a geographic filter, finding drivers within a reasonable radius of the pickup location. This uses the spatial index to query for nearby drivers. The radius might vary based on density; in a city center, you might look within half a mile, while in a suburb, you might look within several miles.

Not all nearby drivers are suitable. Some might already be on a ride. Some might have the wrong vehicle type for the request. Some might have preferences that conflict with the ride. These filters narrow the candidate set.

From the candidates, the system estimates arrival time for each. This is not simply distance divided by speed but a sophisticated routing calculation that considers traffic, road networks, and historical patterns. Estimated arrival time is crucial for both rider experience and driver efficiency.

The selection among candidates considers multiple factors. Arrival time is important, but so is fairness to drivers, ensuring that work is distributed reasonably. Game theory comes into play; if drivers can predict the matching algorithm, they might manipulate their position or behavior. The algorithm must be hard to game while still producing good matches.

The selected driver receives a notification with the ride details. They have a short window to accept. If they decline or do not respond, the system matches with the next-best candidate. This process continues until someone accepts or no candidates remain.

### Handling Driver Acceptance

The acceptance process creates interesting concurrency challenges. While waiting for a driver to respond, other ride requests might arrive. The same driver might be the best match for multiple requests. The system must handle these race conditions gracefully.

One approach reserves a driver when they are offered a ride. During the decision window, they are not offered other rides. This is simple but wastes driver time if riders cancel and reduces matching efficiency if many rides are pending.

Another approach allows a driver to be offered to multiple riders but gives priority based on which request arrived first. If the driver accepts, they are matched with the highest-priority ride, and other riders are rematched. This is more complex but makes better use of supply.

The timeout for driver response is a tuning parameter. Too short, and drivers do not have time to see the offer. Too long, and riders wait impatiently. The optimal timeout might vary by market and situation.

### Pricing and Surge

Dynamic pricing responds to supply and demand imbalance. When demand exceeds supply, prices increase, encouraging more drivers to come online and discouraging marginal demand. This surge pricing is economically efficient but requires careful implementation.

Surge calculation examines supply and demand at a geographic granularity. The city is divided into regions, and each region has its own surge multiplier based on current conditions. These multipliers are recalculated continuously as conditions change.

The surge multiplier affects both the price riders pay and the earnings drivers receive. Higher earnings attract more drivers to surge areas, increasing supply. Higher prices discourage discretionary rides, reducing demand. The market moves toward balance.

Riders must be shown the surge multiplier before confirming their ride. Transparency is important for user trust. Some riders will wait for surge to subside; others will accept the higher price for immediate service.

### Real-Time Updates

Throughout the ride lifecycle, participants need real-time updates. Riders see the driver approaching on a map. Drivers see the route to the pickup and destination. After pickup, both see trip progress.

These real-time updates require efficient data distribution. Traditional request-response patterns do not work well; you do not want the app polling constantly. Instead, persistent connections enable server-pushed updates.

WebSockets or similar technologies maintain connections between apps and servers. When state changes, the server pushes updates through these connections immediately. The challenge is maintaining millions of concurrent connections across many servers.

Connection state must be managed carefully. If a server fails, its connections are lost and must be reestablished. Load balancing must direct reconnecting clients appropriately. Messages sent while disconnected might be queued for delivery or considered lost depending on importance.

### Payments and Ratings

After the ride completes, payment is processed. This is the moment when actual money moves, requiring reliability and accuracy. Payment processing uses many of the patterns discussed elsewhere: idempotency to handle retries, sagas to coordinate with payment providers, queuing to handle temporary failures.

Ratings are collected from both riders and drivers. These ratings feed into matching algorithms, reputation systems, and quality control. Low-rated drivers might receive fewer matches or be removed from the platform. Low-rated riders might find it harder to get rides.

The rating system creates interesting incentive dynamics. Drivers might avoid neighborhoods they perceive as giving low ratings. Riders might feel pressured to rate highly to maintain their own rating. Designing a rating system that produces useful signals while minimizing gaming is an ongoing challenge.

## Case Study Four: Designing a URL Shortening Service

URL shortening might seem simple compared to the previous case studies, but it illustrates important system design principles at a smaller scope. The core problem is straightforward: given a long URL, produce a short code that redirects to it. The challenges lie in scale, performance, and reliability.

### Understanding the Problem

Users submit long URLs and receive short URLs they can share. When someone visits the short URL, they are redirected to the original long URL. The short URLs must be memorable, shareable, and as short as possible.

The scale considerations are significant. A popular URL shortening service might handle billions of redirects per month. Each redirect must be fast because it adds latency to every click. The mapping from short code to long URL must be highly available because downtime means broken links.

Short code generation involves interesting tradeoffs. Shorter codes are better for users but limit the total number of URLs that can be shortened. The character set affects both memorability and length. Collision handling becomes important at scale.

### Short Code Generation

The short code is a compact identifier for the original URL. Several approaches can generate these codes, each with different characteristics.

Sequential integers are the simplest approach. Each new URL receives the next integer: one, two, three, and so on. These integers are encoded in a base higher than ten to make them shorter; using letters and digits gives base sixty-two, making codes significantly shorter than decimal.

Sequential codes have a problem: they are predictable. If you know a code, you can guess nearby codes and discover what URLs others have shortened. This might reveal information that users expected to be private. It also enables enumeration attacks where someone systematically fetches all shortened URLs.

Random codes avoid predictability. Each new URL receives a random string. With sufficient length and randomness, collisions are negligible. Users cannot guess other codes. The downside is that random codes might be longer and are certainly less memorable.

Hashing the original URL creates deterministic codes. The same long URL always produces the same short code, which is useful for deduplication. If someone has already shortened a URL, returning the existing code rather than creating a new one saves space. The challenge is that hash collisions are possible, and handling them adds complexity.

The choice of code length involves a tradeoff. Longer codes support more unique URLs but are harder to remember and share. A seven-character code using base sixty-two supports over three trillion combinations, far more than enough for any realistic scale. Six characters support about fifty-six billion, which might still be sufficient.

### Storage and Retrieval

The core data structure is a mapping from short code to long URL. This is a simple key-value pattern, but the scale and performance requirements constrain the implementation.

A key-value store, whether a traditional database or a dedicated system like Redis or DynamoDB, is well-suited to this access pattern. Short codes are looked up by exact match, which key-value stores optimize for. There is no need for complex queries or joins.

Read operations vastly outnumber writes. A URL might be shortened once but clicked thousands of times. This read-heavy workload benefits from aggressive caching. Most lookups can be served from memory without touching persistent storage.

The storage must be durable. Losing the mapping means broken short URLs, which is unacceptable. Replication and regular backups ensure that data survives failures.

As scale grows, the storage must be sharded. Sharding by short code distributes load evenly because codes are designed to be uniform. Each shard handles a portion of the code space.

### Caching for Performance

The redirect operation must be as fast as possible. Each redirect adds latency to the user's journey. Aggressive caching minimizes this latency.

An in-memory cache holds mappings for frequently accessed short codes. Popular URLs might be accessed millions of times; serving them from memory is orders of magnitude faster than disk. A cache miss falls through to the persistent store.

The caching strategy can be simple for this use case. Mappings are essentially immutable; once created, they do not change. There is no cache invalidation problem because the data does not update. Entries can be cached indefinitely or until evicted for space.

Cache sizing balances memory cost against hit rate. The distribution of access frequency is highly skewed; a small percentage of URLs account for most traffic. Even a modest cache can achieve high hit rates by keeping the most popular URLs.

Edge caching through a CDN further reduces latency. The redirect can happen at an edge location near the user rather than at a central data center. Each edge location maintains its own cache of popular mappings.

### Analytics and Tracking

URL shortening services often provide analytics: how many times was a link clicked, from where, when. These analytics are valuable for users but require additional infrastructure.

Click events must be logged with relevant metadata: timestamp, referrer, user agent, geographic location. The logging must not slow down the redirect; users should not wait for analytics processing. Asynchronous logging sends events to a queue for later processing.

The analytics processing pipeline aggregates click events into useful metrics. Total clicks, clicks over time, clicks by geography, clicks by referrer. These aggregations might use stream processing for real-time dashboards or batch processing for historical analysis.

Analytics queries can be complex: show me clicks from the United States last week, grouped by day. These queries benefit from specialized analytics databases that are optimized for aggregation rather than transactional workloads.

### Custom Short URLs and Vanity Codes

Many services allow users to choose their own short codes. A company might want their brand name in the URL. This custom code feature adds complexity.

Custom codes must be checked for availability. Unlike generated codes where collisions are prevented by the generation algorithm, users might request codes that already exist. The system must check and reject duplicates.

Reserved words and offensive terms should be blocked. You do not want random generation to produce an offensive word or a user to claim an important system path. Maintaining a blocklist adds operational complexity but is essential for a public service.

Custom codes might conflict with randomly generated ones. If users can choose any code, you must ensure the random generator does not produce codes that conflict. Separating the namespace, perhaps by length or character set, avoids this conflict.

### Reliability and Failure Handling

Broken short URLs are highly visible failures. If the service is down, every click produces an error. High availability is essential.

Geographic distribution puts the service close to users everywhere and provides redundancy. If one region fails, others continue serving. DNS-based routing directs users to healthy regions.

The service has minimal dependencies, which simplifies reliability. Reading a mapping from a key-value store does not require complex multi-service coordination. This simplicity makes the redirect path highly resilient.

Write operations, creating new short URLs, can tolerate more latency than redirects. If the write path is temporarily unavailable, users can retry. The redirect path must always work because broken links affect not just the shortener's users but everyone who clicks.

### Expiration and Cleanup

Short URLs create obligations. As long as they exist, you must support them. This creates unbounded storage growth over time.

Some services expire URLs after a period of inactivity. If a URL has not been clicked in a year, it might be deleted, freeing the code for reuse. Users are warned about expiration policies when shortening.

Other services commit to permanent URLs. The URL you create today will work forever. This is attractive to users but commits the service to indefinite storage. The economics must work at any scale.

Deletion requests add another form of cleanup. Users might want to remove URLs they have shortened. Legal requirements might force removal. The system must support deletion while handling the edge cases it creates, like cached mappings that continue to redirect temporarily after deletion.

## Cross-Cutting Lessons

These case studies, while different in their specific challenges, share common themes that appear throughout system design.

Scale changes everything. Approaches that work beautifully at small scale become impossible at large scale. The pull model for timelines works for a personal blog but fails for Twitter. The intuition developed working on small systems must be recalibrated for large ones.

Tradeoffs are unavoidable. Every design decision involves giving something up to gain something else. Push versus pull trades write amplification for read latency. Eventual consistency trades simplicity for availability. Caching trades freshness for speed. There is no design that wins on every dimension.

Specialized components emerge. As systems grow, general-purpose solutions give way to specialized ones. Generic databases are replaced by purpose-built storage. Monolithic applications are decomposed into focused services. This specialization enables optimization but adds operational complexity.

The user experience drives requirements. Technical constraints matter, but ultimately the goal is serving users well. Latency requirements come from user expectations. Reliability requirements come from user impact. Understanding what users actually need helps prioritize the endless possible improvements.

Iteration is essential. No design survives contact with reality unchanged. Traffic patterns differ from predictions. User behavior surprises. New requirements emerge. The best architectures are those that can evolve gracefully as understanding improves.

These case studies provide concrete examples of system design in practice. They show how abstract principles apply to real problems and how successful systems balance competing concerns. Studying them builds intuition that applies far beyond these specific domains.
