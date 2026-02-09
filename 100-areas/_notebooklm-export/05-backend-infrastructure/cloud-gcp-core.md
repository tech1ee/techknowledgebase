# GCP Core Services: Google's Cloud Platform Architecture

## Google Cloud's Distinctive Approach

Google Cloud Platform emerged from Google's decades of experience building and operating some of the world's largest distributed systems. The technologies that power Google Search, Gmail, YouTube, and other massive-scale services form the foundation of GCP. This heritage gives GCP distinctive strengths, particularly in data analytics, machine learning, and container orchestration, where Google's internal expertise translates into compelling cloud offerings.

The philosophy of GCP differs subtly from other cloud providers. Google tends to offer fewer services, but those services often integrate more deeply with each other. Where AWS might offer multiple database services for different use cases, GCP more often provides a single service that addresses multiple use cases through configuration. This approach can reduce the cognitive load of choosing between services but may offer less flexibility for specialized requirements.

GCP organizes resources around projects, which serve as the fundamental unit of organization and billing. Every resource belongs to a project, and IAM policies, billing, and quotas are typically managed at the project level. Organizations can contain multiple projects, with folder hierarchies for additional organization. This structure differs from AWS's account-based model and affects how multi-tenant architectures are designed.

Global infrastructure in GCP emphasizes a global network that Google operates. GCP regions and zones follow the now-standard model of regions containing multiple availability zones, but Google's private network backbone enables capabilities like global load balancing that routes users to the nearest healthy region automatically. This network infrastructure underlies many GCP services and provides performance advantages for globally distributed applications.

## Compute Engine: Virtual Machines on Google Infrastructure

Compute Engine provides virtual machines running on Google's infrastructure, the foundational compute service in GCP. Like EC2 in AWS, Compute Engine gives you control over virtual machines that you configure and manage. The VMs run on the same infrastructure that powers Google's own services, providing access to high-performance networking and storage.

Machine types determine the compute resources available to a VM. GCP offers predefined machine types in several families: general-purpose machines balance compute, memory, and networking; compute-optimized machines provide high-performance processors; memory-optimized machines offer high memory-to-CPU ratios. Custom machine types allow specifying exact CPU and memory combinations, providing flexibility that predefined types do not.

The naming convention for machine types encodes these characteristics. For example, n2-standard-8 indicates an N2 generation general-purpose machine with standard specifications and eight vCPUs. Understanding this naming helps quickly identify appropriate machine types for different workloads.

Images define the operating system and software installed on a VM. GCP provides public images for common operating systems including various Linux distributions and Windows Server. Custom images can be created from existing VMs, enabling consistent deployment of configured systems. Image families group related images, allowing you to specify the family to get the latest image.

Persistent disks provide block storage for VMs. Standard persistent disks use hard disk drives and are appropriate for large, sequential workloads. SSD persistent disks provide higher performance for demanding workloads. Local SSDs provide even higher performance but are ephemeral, attached directly to the host machine rather than network-attached.

Instance groups manage collections of VMs as a unit. Managed instance groups use instance templates to create identical VMs and can automatically scale, update, and heal the group. Unmanaged instance groups are collections of manually created VMs that can be used as backends for load balancers.

Preemptible VMs and spot VMs offer significant discounts in exchange for the possibility that Google may terminate them when capacity is needed. Preemptible VMs have a maximum lifetime of 24 hours, while spot VMs do not. Both are suitable for fault-tolerant workloads like batch processing and can reduce compute costs substantially.

Sole-tenant nodes provide physical servers dedicated to a single customer. This addresses compliance requirements that mandate isolation from other tenants and enables licensing requirements that depend on physical cores.

## Cloud Storage: Object Storage at Scale

Cloud Storage is GCP's object storage service, providing durable, highly available storage for any amount of data. Like S3, Cloud Storage stores objects in buckets, with each object identified by a unique key. The service is designed for eleven nines of durability, ensuring that data is extremely unlikely to be lost.

Storage classes optimize cost based on access patterns. Standard storage is for frequently accessed data, with the lowest access costs but higher storage costs. Nearline storage is for data accessed less than once per month, with lower storage costs but charges for data retrieval. Coldline storage is for data accessed less than once per quarter, with even lower storage costs. Archive storage is for data accessed less than once per year, with the lowest storage costs but higher retrieval costs and a longer minimum storage duration.

Dual-region and multi-region buckets provide geographic redundancy. A dual-region bucket stores data in two specific regions, providing recovery if one region fails. A multi-region bucket stores data in a geographic area like US or EU, automatically distributing across regions in that area. These options trade higher costs for increased availability and durability.

Object lifecycle management automates transitions between storage classes and deletion based on age or access patterns. A lifecycle rule might move objects to Nearline after 30 days, to Coldline after 90 days, and delete them after one year. This automation optimizes costs without manual intervention.

Object versioning preserves every version of objects, protecting against accidental deletion or overwrites. When versioning is enabled, overwriting or deleting an object creates a new version rather than removing the original. Versions can be restored or permanently deleted as needed.

Uniform bucket-level access simplifies access control by requiring all access to be managed through Cloud IAM rather than ACLs. This is the recommended access control approach for most use cases, providing clearer and more consistent security.

Signed URLs provide time-limited access to objects without requiring the requestor to have Cloud Storage permissions. A signed URL includes a cryptographic signature that grants temporary access, useful for allowing downloads without exposing permanent credentials.

Transfer services facilitate moving data into Cloud Storage from various sources. Transfer Service for Cloud Data moves data from other cloud providers. Transfer Appliance is a physical device for transferring very large amounts of data when network transfer would be too slow.

## Cloud SQL and Cloud Spanner: Managed Relational Databases

Cloud SQL provides managed relational databases for MySQL, PostgreSQL, and SQL Server. Like RDS in AWS, Cloud SQL handles administrative tasks like patching, backups, and replication, allowing you to focus on your data and queries rather than database administration.

Instance configuration determines the compute and storage resources available to the database. You select a machine type for CPU and memory, then configure storage type and size separately. Storage can be SSD or HDD and can be configured to automatically grow as data increases.

High availability is achieved through regional configuration with failover to a standby in a different zone. When the primary instance becomes unavailable, Cloud SQL automatically fails over to the standby. This provides protection against zone failures with minimal manual intervention.

Read replicas provide horizontal scaling for read-heavy workloads. Replicas receive changes from the primary asynchronously and can serve read queries, distributing load across multiple instances. Cross-region replicas provide disaster recovery capability and can serve reads closer to users in other regions.

Private IP configuration keeps database traffic within your VPC, never traversing the public internet. This improves security and can improve performance. Public IP access is available when needed, protected by SSL and IP allowlists.

Cloud Spanner is a different kind of relational database, providing a globally distributed, strongly consistent database. Spanner combines the relational model and SQL with horizontal scalability and global distribution. It provides strong consistency across regions through TrueTime, Google's proprietary time synchronization technology.

Spanner is appropriate for workloads that require global distribution with strong consistency, high availability, and horizontal scalability. Financial services, inventory systems, and other applications that cannot tolerate eventual consistency are common use cases. The tradeoff is cost: Spanner is significantly more expensive than Cloud SQL.

## BigQuery: Serverless Data Analytics

BigQuery is GCP's serverless data warehouse, designed for analyzing large datasets using SQL. Rather than provisioning and managing database infrastructure, you load data into BigQuery and query it directly. BigQuery automatically handles resource allocation, scaling to petabyte-scale analyses without capacity planning.

The architecture of BigQuery separates storage from compute. Data is stored in a columnar format optimized for analytical queries. When you run a query, BigQuery allocates compute resources to process it, scanning only the columns needed for the query. You are charged for the amount of data scanned, incentivizing schema design and query writing that minimizes scanned data.

Tables are the basic unit of storage in BigQuery. Tables belong to datasets, which belong to projects. Tables can be loaded from Cloud Storage, streamed in real time, or created from query results. Partitioned tables organize data by date or other columns, allowing queries to scan only relevant partitions. Clustered tables physically organize data by specified columns, improving query performance for filters on those columns.

Querying uses standard SQL with extensions for BigQuery-specific features. The query editor in the console shows the estimated data scan before running, helping manage costs. Query results can be written to new tables, exported to Cloud Storage, or returned directly.

Federated queries allow querying data in Cloud Storage, Cloud SQL, or Cloud Bigtable without loading it into BigQuery. This is useful for ad-hoc analysis of data in its original location or for combining data from multiple sources.

BigQuery ML enables building and deploying machine learning models using SQL. You can create models directly from SQL queries without needing to export data or learn ML frameworks. This democratizes machine learning for analysts familiar with SQL.

Pricing models offer flexibility. On-demand pricing charges per query based on data scanned. Flat-rate pricing provides dedicated capacity for a fixed price, suitable for heavy, predictable query workloads. Understanding your query patterns helps choose the appropriate pricing model.

## VPC Network and Cloud Load Balancing

Virtual Private Cloud in GCP provides isolated virtual networks where GCP resources run. VPC concepts in GCP are similar to other clouds but with some distinctive characteristics.

VPC networks in GCP are global, spanning all regions. This differs from AWS where VPCs are regional. Subnets within a GCP VPC are regional, existing in a specific region but able to span zones within that region. This structure simplifies cross-region networking within a single VPC.

Firewall rules in GCP operate at the VPC level and apply to instances based on network tags or service accounts. Rules specify allowed or denied traffic by protocol, port, and source or destination. Unlike AWS security groups, GCP firewall rules can specify denied traffic, enabling explicit blocking.

Private Google Access allows resources in a subnet to reach Google APIs and services without public IP addresses. This keeps traffic on Google's network rather than traversing the public internet, improving security and potentially performance.

Cloud NAT provides outbound connectivity for resources without public IPs. Like NAT gateways in other clouds, Cloud NAT allows resources to initiate connections to the internet while remaining unreachable from the internet. Cloud NAT is a managed service that automatically scales.

VPC Network Peering connects VPC networks, allowing resources in each to communicate privately. Peering can be within a project, across projects, or even across organizations. Shared VPC is another option that allows a VPC in one project to be used by resources in other projects, simplifying network management in multi-project environments.

Cloud Load Balancing provides global and regional load balancing options. Global load balancing routes users to the nearest healthy region using Google's global network, providing low latency for globally distributed applications. Regional load balancing distributes traffic within a region.

HTTP(S) Load Balancing operates at layer 7, supporting content-based routing, SSL termination, and integration with Cloud CDN and Cloud Armor. TCP/UDP Load Balancing operates at layer 4 for non-HTTP traffic. Internal Load Balancing provides load balancing for traffic within your VPC.

## Cloud IAM: Identity and Access Management

Cloud IAM controls access to GCP resources. Every API call is authenticated and authorized through IAM. Understanding IAM is essential for security and for enabling services to interact with each other.

IAM in GCP follows a resource hierarchy. Permissions can be granted at the organization, folder, project, or individual resource level. Permissions granted at higher levels are inherited by lower levels, so a permission granted at the organization level applies to all projects and resources in the organization.

Principals are identities that can be granted access. Google accounts are for individual users. Service accounts are for applications and services. Google groups allow managing permissions for multiple users together. Cloud Identity domains allow managing users and groups for an organization.

Roles are collections of permissions. Primitive roles are the legacy roles of Owner, Editor, and Viewer that apply across a project. Predefined roles are maintained by Google and provide granular permissions for specific services. Custom roles allow defining exactly the permissions needed when predefined roles are not a good fit.

Policies bind principals to roles on resources. A policy specifies that a particular principal has a particular role on a particular resource. Policies are additive—if any policy grants a permission, the principal has that permission. There is no explicit deny in GCP IAM policies at the project level, though organization policies can restrict actions.

Service accounts are identities for applications and services. Each service account has an email address that identifies it. Service accounts can be granted IAM roles like any other principal. When applications run on GCP resources, they can use the associated service account to make API calls without managing credentials explicitly.

Workload identity federation allows applications outside GCP to access GCP resources without service account keys. External identities from providers like AWS, Azure, or OIDC providers can be mapped to GCP principals, enabling secure access from hybrid and multi-cloud environments.

## Google Kubernetes Engine

Google Kubernetes Engine, or GKE, provides managed Kubernetes clusters on GCP. Given that Google created Kubernetes based on its internal container orchestration system, GKE is often considered the most mature and capable managed Kubernetes offering.

GKE handles the Kubernetes control plane as a managed service. The API server, controller manager, scheduler, and etcd are managed by Google with high availability and automatic upgrades. You focus on your workloads running on worker nodes.

Node pools group nodes with similar configuration. A cluster can have multiple node pools with different machine types, different auto-scaling settings, or different workload characteristics. Node pools can be added, modified, and removed without affecting the cluster or other node pools.

Autopilot is a mode of operation where Google manages not just the control plane but also the nodes. You deploy pods, and GKE provisions appropriate nodes automatically. This mode provides a more serverless experience for Kubernetes while maintaining compatibility with standard Kubernetes APIs.

Cluster networking in GKE can use VPC-native mode, where pods receive IP addresses from your VPC, enabling them to communicate directly with other VPC resources. Alternatively, routes-based mode uses GCP routes to direct traffic to pods. VPC-native mode is recommended for most new clusters.

Private clusters keep nodes and optionally the control plane off the public internet. Nodes have only private IP addresses and access the internet through Cloud NAT if needed. The control plane can be made accessible only through authorized networks.

Workload Identity links Kubernetes service accounts to GCP service accounts, allowing pods to access GCP APIs securely without managing service account keys. This is the recommended way to provide GCP credentials to workloads running on GKE.

Binary Authorization enforces policies about which container images can run on your cluster. You can require that images are signed by trusted authorities, built by specific pipelines, or scanned for vulnerabilities. This provides additional security for your container supply chain.

## Cloud Functions and Cloud Run

Cloud Functions provides serverless compute for event-driven workloads. You write functions in supported languages that run in response to events. Cloud Functions handles all infrastructure, automatically scaling from zero to handle incoming events.

Functions are triggered by events from various sources. HTTP triggers respond to HTTP requests, creating simple APIs. Pub/Sub triggers respond to messages on Pub/Sub topics. Cloud Storage triggers respond to object creation, deletion, or modification. Firebase triggers respond to changes in Firebase databases. Each trigger type provides context about the event to the function.

The execution environment provides the runtime and dependencies for your function. Cloud Functions supports Node.js, Python, Go, Java, and other languages. Functions receive event data and context as parameters and return a response. The environment includes temporary storage and network access to other GCP services.

Cloud Run provides serverless containers, extending serverless beyond functions to any containerized application. You provide a container image, and Cloud Run handles deploying and scaling it. Cloud Run scales to zero when there is no traffic and scales up automatically when requests arrive.

The container contract for Cloud Run requires that containers listen on a port specified by the PORT environment variable and respond to HTTP requests. Beyond that, containers can run any application that can be containerized. This makes Cloud Run suitable for web applications, APIs, and background workers.

Cloud Run services receive traffic at URLs automatically provisioned by Cloud Run. Traffic splitting allows gradually shifting traffic between revisions, enabling canary deployments and rollbacks. Custom domains can be mapped to services.

Cloud Run jobs run containers to completion rather than serving requests. Jobs are appropriate for batch processing, scheduled tasks, and other workloads that should run once rather than continuously. Jobs can be triggered manually, on a schedule, or from other events.

GCP's core services provide a foundation for building cloud applications, with strengths in data analytics, machine learning, and container orchestration reflecting Google's heritage. Understanding these services enables effective use of GCP and informed architectural decisions.
