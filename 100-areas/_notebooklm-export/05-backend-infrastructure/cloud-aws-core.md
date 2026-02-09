# AWS Core Services: Building Blocks of Cloud Architecture

## The AWS Ecosystem and Its Evolution

Amazon Web Services launched in 2006 with a simple premise: the infrastructure Amazon had built for its e-commerce platform could be offered to others. What began with basic storage and compute services has grown into a vast ecosystem of over two hundred services spanning compute, storage, databases, networking, machine learning, analytics, and much more. AWS pioneered many cloud computing concepts and remains the market leader, making familiarity with its core services essential for anyone working in cloud infrastructure.

The philosophy underlying AWS is that of building blocks. Rather than providing a few monolithic solutions, AWS offers a large number of specialized services that can be combined to build virtually any architecture. This approach provides flexibility and allows customers to select exactly the services they need, but it also creates complexity. Understanding which services to use for which purposes, and how they interact, is a significant part of working effectively with AWS.

AWS organizes services by category, but many services span multiple categories or do not fit neatly into any single one. Compute services run workloads. Storage services persist data. Database services manage structured data. Networking services connect resources. Security services protect them. Management services monitor and operate them. The core services described here form the foundation upon which more specialized services are built.

The pricing model of AWS is predominantly pay-as-you-go, with costs varying by service, usage pattern, and configuration. Reserved capacity offers discounts for commitment, spot instances offer discounts for interruptible capacity, and savings plans provide flexible discount options. Understanding pricing is essential for managing cloud costs, and the AWS pricing calculator and cost explorer tools help estimate and track spending.

## EC2: Elastic Compute Cloud

EC2, the Elastic Compute Cloud, is AWS's foundational compute service, providing virtual machines that run on AWS's infrastructure. An EC2 instance is a virtual server that you control completely, from the operating system through the applications running on it. Understanding EC2 is fundamental because many other AWS services are built on top of EC2 or integrate closely with it.

Instance types determine the hardware characteristics of EC2 instances. AWS offers hundreds of instance types optimized for different use cases. General-purpose instances provide a balance of compute, memory, and networking. Compute-optimized instances have high-performance processors for compute-intensive workloads. Memory-optimized instances have large amounts of memory for databases and caching. Storage-optimized instances have high disk throughput. Accelerated computing instances include GPUs or specialized hardware for machine learning and high-performance computing.

The instance type naming convention encodes these characteristics. The first letter indicates the instance family, such as m for general-purpose, c for compute-optimized, or r for memory-optimized. A number indicates the generation. Additional letters might indicate variations like ARM processors, local storage, or networking enhancements. The final element indicates the size within the family.

Amazon Machine Images, or AMIs, define what software is installed on an instance at launch. An AMI includes the operating system, any pre-installed software, and configuration. AWS provides public AMIs for common operating systems and software stacks. The AWS Marketplace offers commercial AMIs from third-party vendors. You can create custom AMIs from your running instances, capturing your configuration for reproducible deployments.

Instance lifecycle includes launching, running, stopping, and terminating. A running instance consumes compute resources and incurs charges. A stopped instance releases compute resources but retains its attached storage, incurring only storage charges. A terminated instance is deleted, releasing all resources. Understanding these states is important for cost management and for designing resilient systems.

Placement groups control how instances are distributed across underlying hardware. Cluster placement groups place instances close together for low-latency networking. Spread placement groups distribute instances across distinct hardware to reduce correlated failures. Partition placement groups divide instances into groups that do not share hardware.

Auto Scaling Groups automatically adjust the number of EC2 instances based on demand. You define scaling policies that specify conditions for scaling out or in, and the Auto Scaling Group creates or terminates instances accordingly. Launch templates specify the configuration for new instances, including instance type, AMI, and networking settings. Auto Scaling integrates with Elastic Load Balancing to route traffic to healthy instances.

## S3: Simple Storage Service

S3 is AWS's object storage service, providing highly durable, scalable storage for any amount of data. S3 stores objects, which are files plus metadata, in buckets. Each object has a unique key within its bucket, which combined with the bucket name and region provides a unique identifier for accessing the object.

The durability and availability of S3 are among its most important properties. Standard storage is designed for eleven nines of durability, meaning that statistically, if you store ten million objects, you might lose one every ten thousand years. Availability, meaning the ability to access objects when requested, is typically around four nines for standard storage. These properties make S3 suitable for primary storage of critical data.

Storage classes allow optimizing cost based on access patterns. S3 Standard is the default, providing high availability and low latency. S3 Intelligent-Tiering automatically moves objects between access tiers based on actual access patterns. S3 Standard-IA, for infrequent access, offers lower storage costs with higher retrieval costs. S3 Glacier and Glacier Deep Archive provide very low storage costs for archival data, with retrieval times ranging from minutes to hours.

Bucket policies and access control lists control who can access S3 buckets and objects. By default, buckets and objects are private. Access can be granted to specific AWS accounts, to specific IAM users and roles, or to the public. S3 Access Points provide simplified access management for applications accessing buckets from VPCs.

Versioning preserves every version of every object in a bucket. When versioning is enabled, modifying or deleting an object creates a new version rather than overwriting or removing the original. This provides protection against accidental deletion or overwrites and enables point-in-time recovery.

S3 Lifecycle policies automate transitions between storage classes and object deletion. A policy might move objects to infrequent access storage after thirty days, to Glacier after ninety days, and delete them after a year. Lifecycle policies help optimize costs without manual intervention.

Cross-region replication copies objects from one bucket to another in a different region, providing disaster recovery and compliance with data residency requirements. Same-region replication can aggregate data from multiple buckets or maintain a backup copy in the same region.

S3 Transfer Acceleration speeds up uploads to S3 by routing data through AWS edge locations. For large files uploaded from distant locations, Transfer Acceleration can significantly reduce upload times.

## RDS: Relational Database Service

RDS is a managed service for running relational databases in AWS. Rather than installing and operating database software on EC2 instances, RDS handles the administrative tasks: provisioning, patching, backup, recovery, and maintenance. You manage your database schema and queries; AWS manages the database infrastructure.

RDS supports multiple database engines. MySQL, PostgreSQL, and MariaDB are open-source engines with broad compatibility. Oracle and SQL Server are commercial engines with licensing managed through AWS or brought from existing licenses. Amazon Aurora is AWS's proprietary engine, compatible with MySQL or PostgreSQL but with enhanced performance and availability.

Instance classes for RDS, like EC2, determine the compute and memory available to the database. Database storage uses EBS volumes, with options for SSD-backed general-purpose storage, provisioned IOPS for demanding workloads, or magnetic storage for infrequently accessed data.

Multi-AZ deployments provide high availability by maintaining a synchronous standby replica in a different availability zone. If the primary instance fails, RDS automatically fails over to the standby, typically within a minute or two. Applications connected to the RDS endpoint automatically connect to the new primary.

Read replicas provide horizontal scaling for read-heavy workloads. A read replica is an asynchronous copy of the primary database that can serve read queries. You can have multiple read replicas, distribute read traffic across them, and even create read replicas in different regions for geographic distribution.

Automated backups create daily snapshots and retain transaction logs, enabling point-in-time recovery to any second within the retention period. Manual snapshots persist until explicitly deleted, providing long-term backup retention.

Parameter groups customize database configuration. Rather than editing configuration files directly, you modify parameter groups that RDS applies to database instances. This separation ensures consistent configuration across instances and regions.

Security integrates with AWS identity and access management. Database instances run in VPCs and can be configured to accept connections only from specific security groups or networks. Encryption at rest and in transit protects data confidentiality.

## Lambda: Serverless Compute

Lambda represents a different model of compute than EC2. Rather than provisioning and managing servers, you provide code that Lambda runs in response to events. Lambda handles all infrastructure concerns: provisioning capacity, scaling to handle load, and managing the runtime environment. You pay only for the compute time consumed during function execution.

Lambda functions are the unit of deployment. A function is code in a supported language, packaged with any dependencies, configured with memory and timeout settings, and triggered by events. Functions should be focused, performing a single task, and should complete quickly—the maximum execution time is fifteen minutes, but functions typically run for seconds or less.

Triggers determine when Lambda functions run. API Gateway can trigger functions in response to HTTP requests, creating serverless APIs. S3 can trigger functions when objects are created or modified. CloudWatch Events and EventBridge can trigger functions on schedules or in response to AWS events. Many other AWS services can trigger Lambda functions, and custom applications can invoke functions directly.

The execution environment provides the runtime and context for function code. Lambda supports multiple runtimes including Node.js, Python, Java, Go, Ruby, and .NET. Custom runtimes allow running other languages. The environment includes temporary storage, environment variables, and context information about the invocation.

Cold starts occur when Lambda needs to provision a new execution environment. The first invocation after a period of inactivity, or when scaling up to handle more concurrent invocations, incurs additional latency while the environment is prepared. Provisioned concurrency keeps environments warm, eliminating cold starts at the cost of paying for the reserved capacity.

Concurrency controls limit how many function instances can run simultaneously. By default, Lambda scales automatically to handle incoming requests, but you can set reserved concurrency to guarantee capacity for a function or limit concurrency to prevent overwhelming downstream resources.

Lambda integrates deeply with other AWS services. IAM roles determine what AWS resources functions can access. CloudWatch provides logs and metrics. X-Ray provides distributed tracing. Step Functions orchestrates multiple Lambda functions into workflows.

## VPC: Virtual Private Cloud

VPC is the networking layer of AWS, providing isolated virtual networks where you launch AWS resources. Understanding VPC is essential because almost all AWS resources that communicate over networks run within VPCs.

A VPC spans a region and has an IP address range that you specify in CIDR notation. This address range is divided into subnets, each of which exists in a specific availability zone. Resources launched in a subnet receive IP addresses from the subnet's range.

Public subnets have routes to the internet through an internet gateway. Resources in public subnets can communicate with the public internet if they have public IP addresses or elastic IP addresses. Private subnets do not have routes to the internet gateway, isolating resources from public internet access.

NAT gateways allow resources in private subnets to initiate connections to the internet while remaining unreachable from the internet. A NAT gateway sits in a public subnet and translates outbound traffic from private subnets, allowing responses to return while blocking unsolicited inbound connections.

Route tables determine how traffic is routed within and between subnets and to destinations outside the VPC. Each subnet is associated with a route table. The route table contains rules that direct traffic based on destination IP address.

Security groups provide stateful firewall rules at the resource level. Each security group defines rules for inbound and outbound traffic based on protocol, port, and source or destination. Security groups are stateful, meaning return traffic for allowed connections is automatically permitted.

Network access control lists provide stateless firewall rules at the subnet level. Unlike security groups, NACL rules must explicitly allow both inbound and outbound traffic. NACLs are evaluated in order, with the first matching rule applied.

VPC peering connects two VPCs, allowing resources in each to communicate as if they were on the same network. Peering can be within a region or between regions. Transit gateways provide a hub for connecting multiple VPCs and on-premises networks at scale.

VPC endpoints enable private connectivity to AWS services without traversing the public internet. Gateway endpoints provide private routes to S3 and DynamoDB. Interface endpoints use PrivateLink to create private connections to many other AWS services.

## IAM: Identity and Access Management

IAM controls access to AWS resources. Every API call to AWS is authenticated and authorized through IAM. Understanding IAM is essential for security and for enabling resources to interact with each other.

Users are identities for humans or applications that interact with AWS. Users authenticate with access keys or passwords and can have permissions assigned directly or through group membership. Best practices include using individual users rather than shared accounts, enabling multi-factor authentication, and rotating credentials regularly.

Groups collect users with similar permissions. Permissions are assigned to groups, and users inherit the permissions of groups they belong to. This simplifies permission management and ensures consistency across users with similar roles.

Roles provide temporary credentials for assuming a set of permissions. Applications running on AWS resources typically use roles rather than user credentials. When an EC2 instance or Lambda function assumes a role, it receives temporary credentials that it uses to make API calls. Roles can also allow cross-account access or federation with external identity providers.

Policies define what actions are allowed or denied on which resources. Policies use a JSON format that specifies effect, actions, resources, and conditions. Policies can be attached to users, groups, or roles. AWS provides managed policies for common use cases, and you can create custom policies for specific requirements.

The principle of least privilege means granting only the permissions required for a task. Overly permissive policies create security risks. IAM Access Analyzer helps identify resources shared externally and permissions that are not being used.

Service control policies apply to AWS Organizations and can restrict what actions are available within an organizational unit. Even if an IAM policy grants permission, a service control policy can override it. This provides guardrails across accounts in an organization.

## Elastic Load Balancing

Load balancers distribute traffic across multiple targets, improving availability and enabling scaling. AWS offers several types of load balancers, each suited for different use cases.

Application Load Balancers operate at layer 7, the application layer, and are suited for HTTP and HTTPS traffic. They support content-based routing, directing requests to different target groups based on path, host header, or other HTTP attributes. Application Load Balancers integrate with AWS WAF for web application firewall protection.

Network Load Balancers operate at layer 4, the transport layer, and are suited for TCP, UDP, and TLS traffic. They can handle millions of requests per second with ultra-low latency. Network Load Balancers are appropriate for non-HTTP workloads and for scenarios requiring extreme performance.

Gateway Load Balancers are designed for deploying virtual appliances like firewalls and intrusion detection systems. They operate at layer 3 and allow inserting network appliances transparently into the traffic path.

Target groups define the destinations that receive traffic from a load balancer. Targets can be EC2 instances, IP addresses, Lambda functions, or other load balancers. Health checks verify that targets are able to handle traffic, and unhealthy targets are automatically removed from rotation.

Listeners define how the load balancer receives traffic. A listener has a protocol and port and routes matching traffic according to rules. HTTPS listeners terminate TLS connections, using certificates from AWS Certificate Manager.

## Integrating Core Services

Real-world architectures combine these core services into cohesive systems. Understanding common integration patterns helps in designing effective architectures.

A typical web application might use EC2 instances behind an Application Load Balancer, with an RDS database for structured data and S3 for static assets and user uploads. The application runs in private subnets, reachable only through the load balancer. The database runs in private subnets, reachable only from the application instances.

A serverless application might use API Gateway to receive HTTP requests, Lambda functions to process them, and DynamoDB for data storage. S3 might store larger objects or host a static website frontend. This architecture requires no server management and scales automatically with demand.

Event-driven architectures use Lambda functions triggered by events from various sources. S3 events trigger processing of uploaded files. SQS messages trigger asynchronous task processing. CloudWatch Events trigger scheduled jobs. This pattern enables loosely coupled systems that scale independently.

Data processing pipelines might use S3 as a data lake, Lambda or EMR for transformation, and RDS or Redshift for queryable storage. EventBridge or Step Functions orchestrate the flow of data through processing stages.

These patterns are starting points, not prescriptions. AWS's building-block philosophy means there are many ways to architect any given system. The choice depends on requirements for performance, cost, operational simplicity, and many other factors. Mastering the core services provides the foundation for making these architectural decisions effectively.
