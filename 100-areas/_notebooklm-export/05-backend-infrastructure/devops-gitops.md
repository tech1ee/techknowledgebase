# GitOps Principles: Declarative Infrastructure and Continuous Reconciliation

## The Emergence of GitOps

GitOps emerged from the cloud-native community as a set of practices for deploying and operating applications and infrastructure. The term was coined by Weaveworks in 2017, though the underlying ideas had been developing for years in organizations that were pushing the boundaries of infrastructure automation. GitOps represents a convergence of infrastructure as code, declarative configuration, and continuous delivery principles, unified around Git as the single source of truth.

The fundamental insight of GitOps is that Git is not just a place to store code—it can be the authoritative source of truth for your entire system's desired state. If the complete configuration of your infrastructure and applications lives in Git, then Git becomes the interface for making changes to your system. Want to deploy a new version? Make a Git commit. Want to change a configuration? Make a Git commit. Want to roll back? Revert the commit. This simplicity is deceptive; the implications are profound.

Traditional deployment workflows involve pipelines that push changes to production systems. An operator or automated system executes commands to apply changes, and the state of the production system is whatever results from the last set of commands executed. There is no single place to look to understand what the system should look like, and drift between intended and actual state can accumulate without notice.

GitOps inverts this model. Rather than pushing changes to production, GitOps uses agents that pull the desired state from Git and continuously reconcile the actual state to match. The Git repository becomes the source of truth, and the production system is continuously made to match what is in Git. This pull-based model has important properties for security, auditability, and reliability.

The cultural shift that GitOps enables is significant. Developers, who are already fluent in Git, can deploy and operate applications using familiar tools and workflows. Operations becomes more like code review than like command execution. The barrier between development and operations lowers, supporting the DevOps philosophy while providing concrete practices and tools.

## Core Principles of GitOps

Four principles characterize GitOps, each building on the others to create a coherent approach to infrastructure management.

The first principle is that the entire system is described declaratively. Rather than specifying the steps to reach a desired state, you specify the desired state itself. Kubernetes manifests are declarative: they describe what pods, services, and other resources should exist, not how to create them. Terraform configurations are declarative: they describe what infrastructure should exist. Declarative specifications enable the system to determine what changes are needed to reach the desired state from any starting state.

The second principle is that the desired state of the system is versioned in Git. Git provides versioning, audit history, branching, and merging—capabilities that took decades to develop for code but can be applied directly to infrastructure configuration. Every change is a commit with an author, timestamp, and message. The complete history of how the system evolved is preserved. Multiple versions can be compared, branched, and merged using standard Git operations.

The third principle is that approved changes can be automatically applied to the system. When a change is merged to the appropriate branch, the system should automatically update to reflect the new desired state. This automation eliminates manual deployment steps and ensures that the system always reflects what is in Git. The approval process happens through Git mechanisms like pull requests and code review, not through separate deployment approval systems.

The fourth principle is that software agents ensure correctness and alert on divergence. Rather than assuming that the system remains in the desired state after changes are applied, GitOps uses agents that continuously compare actual state to desired state. If the states differ—whether due to manual changes, failed deployments, or external factors—the agent either corrects the drift or alerts operators. This continuous reconciliation is what makes GitOps robust against configuration drift.

## The Pull-Based Deployment Model

The distinction between push-based and pull-based deployment is central to understanding GitOps. Traditional CI/CD systems use push-based deployment: a pipeline running outside the cluster executes commands to apply changes to the cluster. GitOps uses pull-based deployment: an agent running inside the cluster monitors the Git repository and applies changes when it detects differences.

Push-based deployment requires the CI/CD system to have credentials for the production cluster. If the CI/CD system is compromised, the attacker gains access to production. Push-based deployment also requires network connectivity from the CI/CD system to the production cluster, which may be challenging for clusters in restricted networks.

Pull-based deployment requires only that the agent inside the cluster can reach the Git repository, which is typically outbound HTTPS access. The credentials for production resources stay inside the cluster, reducing the attack surface. Even if the Git repository is compromised, the attacker gains only the ability to change the desired state; they do not gain direct access to the cluster.

The pull model also handles disconnection gracefully. If the connection to the Git repository is temporarily unavailable, the agent continues operating based on the last known state and reconciles when connectivity is restored. If the CI/CD system in a push model is unavailable, deployments simply cannot happen until it is restored.

Reconciliation loops are the mechanism that implements pull-based deployment. The agent periodically polls the Git repository, comparing the desired state in Git to the actual state in the cluster. When differences are detected, the agent applies the changes needed to reach the desired state. This loop runs continuously, not just when deployments are triggered.

## ArgoCD: Declarative Continuous Delivery for Kubernetes

ArgoCD is one of the most popular GitOps tools for Kubernetes, providing a rich interface for managing application deployments through Git. It implements the GitOps principles with features designed for enterprise use, including access control, audit logging, and multi-cluster support.

An ArgoCD Application is the core resource that connects a Git repository to a Kubernetes cluster. It specifies the source repository and path containing Kubernetes manifests, the destination cluster and namespace, and policies for how synchronization should occur. The application continuously monitors both Git and the cluster, tracking the sync state between them.

The sync process compares the desired state from Git to the actual state in the cluster and applies the differences. Sync can happen automatically when Git changes are detected, or it can require manual trigger for additional control. Prune options control whether resources that exist in the cluster but not in Git should be deleted, addressing the question of what to do when configuration is removed from Git.

Application health goes beyond whether resources exist to whether they are functioning correctly. ArgoCD understands the health semantics of various Kubernetes resources and provides an overall health status. A deployment is healthy when its pods are running and ready. A service is healthy when it has endpoints. Custom health checks can be defined for resources that ArgoCD does not natively understand.

The sync status indicates whether the cluster matches Git. An application might be synced, meaning actual matches desired, or out of sync, meaning there are differences. Being out of sync is not necessarily a problem—it might mean a new version is waiting to be deployed—but persistent out-of-sync status might indicate problems that need investigation.

The ArgoCD interface provides visibility into applications across the organization. Dashboards show sync and health status at a glance. Drill-down views show individual resources and their status. The diff view shows exactly what would change in a sync operation. This visibility makes it easy to understand the state of deployments without connecting to clusters directly.

## Flux: Kubernetes-Native GitOps

Flux is another major GitOps tool, developed originally by Weaveworks and now part of the Cloud Native Computing Foundation. Flux takes a different architectural approach than ArgoCD, using a set of specialized controllers rather than a monolithic application server.

The source controller watches Git repositories, Helm repositories, and other sources for changes. When changes are detected, it makes the new content available to other controllers. The separation of source management from other concerns allows different sources to be used for different purposes.

The kustomize controller applies Kubernetes manifests, optionally processed through Kustomize for environment-specific customization. Kustomize allows base manifests to be modified for different environments without duplicating the entire configuration. This is particularly useful when the same application is deployed to multiple environments with minor differences.

The helm controller manages Helm releases, allowing Helm charts to be deployed through the GitOps workflow. The Helm release configuration is stored in Git, and the controller ensures the cluster matches that configuration. This brings Helm into the GitOps model while preserving Helm's templating and packaging capabilities.

Flux's controller-based architecture allows each component to be deployed and scaled independently. Organizations can use only the controllers they need and can customize the behavior of individual controllers without affecting others. This modularity supports diverse use cases and allows Flux to evolve component by component.

Multi-tenancy in Flux is supported through namespaced resources and role-based access control. Different teams can manage different parts of the cluster through different Git repositories, with Flux ensuring each team's changes are applied to their appropriate namespaces. This enables self-service deployment for teams while maintaining overall cluster governance.

## Repository Structure and Organization

How you structure your Git repositories for GitOps affects maintainability, security, and the ability to apply different policies to different environments. Several patterns have emerged, each with tradeoffs.

A single repository containing all configuration is the simplest approach. One repository holds manifests for all applications and all environments. This makes it easy to see everything in one place and to make changes that span multiple applications or environments. However, it can become unwieldy for large organizations and makes it difficult to apply different access controls to different environments.

Separate repositories for applications and environments split concerns. Application repositories contain the manifests for each application, while environment repositories specify which versions of applications are deployed in each environment. This separation allows application teams to own their manifests while a platform team controls what is deployed where.

Repository per environment takes the separation further, with completely separate repositories for development, staging, and production. This allows different access controls, different approval processes, and complete isolation between environments. However, it creates challenges for promoting changes between environments and can lead to drift if the repositories diverge.

Repository per team gives each team their own repository for the applications they own. This supports team autonomy and self-service while limiting the blast radius of mistakes. A platform team typically maintains shared infrastructure in a separate repository.

Monorepo versus polyrepo debates apply to GitOps as they do to application code. Monorepos centralize everything but can become unwieldy. Polyrepos provide isolation but create coordination challenges. Hybrid approaches, like repositories organized by domain or tier, balance these concerns.

Directory structure within repositories matters for organization and for applying policies. Common patterns include directories per environment, directories per application, and directories per cluster. The structure should match how changes flow through your system and how access control is applied.

## Environment Promotion and Workflows

Promoting changes from development through staging to production is a core workflow in GitOps. Several patterns address this workflow while maintaining the Git-centric approach.

Branch-per-environment uses different branches for different environments. The development branch reflects what is deployed in development, staging branch for staging, and main for production. Promoting a change means merging from one branch to another. This approach uses familiar Git merge mechanics but can become complex with long-running branches.

Directory-per-environment uses a single branch but different directories for each environment. Promoting a change means updating the configuration in the target environment's directory. This might be copying files, updating a version reference, or modifying an overlay. The promotion is itself a commit that can be reviewed and audited.

Image tag updates are a common promotion pattern for container-based applications. The application manifest references a container image by tag. Promoting a version means updating the tag in the manifest for each environment. Automation can detect when a new image is available and create pull requests to update the tag.

Automated promotions can advance changes through environments automatically based on policies. A change might be automatically promoted from development to staging after passing tests, then require manual approval to proceed to production. This automation speeds up the promotion pipeline while maintaining control at key decision points.

GitOps tooling supports promotion workflows. ArgoCD's ApplicationSets can define applications across environments with consistent configuration. Flux's notification controller can trigger actions when changes are detected. Pull request automation can create and merge promotion pull requests.

Change verification before promotion ensures that what worked in one environment will work in the next. This might include running integration tests against the staging environment before promoting to production, or performing canary analysis on a production subset before full rollout. GitOps does not eliminate the need for verification; it provides a framework within which verification fits.

## Handling Secrets in GitOps

The principle that everything should be in Git conflicts with the security principle that secrets should not be stored in plain text. This tension requires careful handling, and several approaches have emerged.

Encrypted secrets store secrets in Git but encrypted with a key that is managed separately. Tools like Sealed Secrets, SOPS, and git-crypt encrypt secret values before they are committed. The GitOps agent decrypts them when applying the configuration. This approach maintains the Git-centric model while protecting secret values.

External secrets managers integrate GitOps with external systems like HashiCorp Vault, AWS Secrets Manager, or Azure Key Vault. The Git repository contains references to secrets, not the secrets themselves. The GitOps agent or a separate controller retrieves the actual secret values from the external system. This approach leverages mature secrets management systems but adds operational complexity.

The trade-off between these approaches involves considering who manages the encryption keys or external systems, how secrets are rotated, how access control is enforced, and how secrets are audited. Organizations with mature secrets management may prefer external integration, while others may prefer the simplicity of encrypted secrets.

Secret rotation in GitOps requires updating both the secret value and any applications that use it. With encrypted secrets, this means decrypting with the old key, encrypting with the new key, and committing the change. With external secrets, the secret is rotated in the external system, and the GitOps layer may need to refresh the value.

Limiting secret access ensures that secrets are available only where needed. Kubernetes RBAC can restrict which pods can read which secrets. GitOps access control can restrict who can modify secret references. The principle of least privilege applies to secrets as to other resources.

## Drift Detection and Reconciliation

Configuration drift occurs when the actual state of a system diverges from the desired state. In traditional operations, drift accumulates through manual changes, failed deployments, and forgotten cleanup. GitOps addresses drift through continuous reconciliation.

Detection compares the desired state in Git to the actual state in the cluster. The GitOps agent performs this comparison periodically, typically every few minutes. When differences are detected, they are reported and optionally corrected automatically.

Automatic correction applies changes to bring the actual state back to the desired state. If someone manually changed a configuration in the cluster, the GitOps agent reverts it to match Git. This enforcement ensures that the Git repository remains authoritative, but it can be surprising to operators who expect their manual changes to persist.

Notification of drift alerts operators when differences are detected, without automatically correcting them. This is appropriate for environments where manual changes are sometimes necessary or where automatic correction might cause problems. Operators can investigate the drift and decide whether to correct it or to update Git to reflect the new reality.

Exempting resources from reconciliation is sometimes necessary. Some resources should not be managed through GitOps, or should allow certain fields to be modified externally. GitOps tools provide mechanisms for exempting specific resources or fields from reconciliation.

Understanding why drift occurred is as important as correcting it. Was it a necessary emergency change that should be incorporated into Git? Was it an unauthorized change that indicates a security or process problem? Was it a side effect of some other operation? The investigation informs both the immediate response and longer-term process improvements.

## Multi-Cluster and Multi-Environment GitOps

Organizations often manage multiple Kubernetes clusters across different environments, regions, or purposes. GitOps practices must scale to address this complexity while maintaining the simplicity and auditability benefits.

Cluster inventories define which clusters exist and their properties. This inventory might be in Git as well, enabling GitOps for the clusters themselves, not just the applications running on them. When a new cluster is added to the inventory, GitOps agents can automatically bootstrap it with the appropriate configuration.

Application targeting determines which applications deploy to which clusters. This might be based on environment labels, cluster labels, or explicit enumeration. GitOps tools provide mechanisms for defining these relationships, often with the ability to generate application definitions from templates and lists.

Shared configurations are common across clusters but need to be customized for each. Cluster-specific values like endpoints, sizes, and replicas overlay shared base configurations. Kustomize, Helm values, and similar tools support this layering.

Progressive delivery across clusters enables deploying first to less critical clusters, validating the deployment, then proceeding to more critical clusters. This multi-cluster canary approach limits the blast radius of problems while still enabling automated rollout.

Centralized versus distributed management is a design choice for multi-cluster GitOps. A centralized approach manages all clusters from a single control plane, which simplifies operations but creates a single point of failure. A distributed approach runs GitOps agents on each cluster, improving resilience but complicating coordination.

## Observability and Auditing

GitOps inherently provides some observability and auditing through Git's commit history. Every change is a commit with an author, timestamp, and description. Viewing the Git log shows the complete history of changes to the system. However, additional observability addresses operational needs.

Sync status monitoring shows whether clusters are in sync with Git across the organization. Dashboards aggregate status across applications, clusters, and environments. Alerts notify operators when applications fall out of sync or fail to reach a healthy state.

Deployment tracking correlates changes in Git with changes in the running system. When did a particular change reach production? How long did it take? Were there any issues during rollout? This tracking supports operational understanding and incident investigation.

Audit requirements in regulated environments may exceed what Git logs provide. Additional logging of who approved changes, what policies were evaluated, and what the system looked like before and after changes may be needed. GitOps tools often provide this additional audit logging.

Metrics and dashboards provide quantitative insight into GitOps operations. How frequently are deployments happening? What is the sync latency from commit to deployment? How often do syncs fail? These metrics help identify bottlenecks and improvement opportunities.

## GitOps in Practice: Considerations and Tradeoffs

Adopting GitOps is not without challenges. Understanding the tradeoffs helps organizations make informed decisions and address challenges proactively.

The learning curve for teams unfamiliar with Git, Kubernetes, and declarative configuration can be significant. While GitOps simplifies many operations, it requires new skills and mental models. Investment in training and gradual adoption helps teams build competence.

Emergency changes that bypass GitOps processes are sometimes necessary. When production is down and the fix requires a change, waiting for pull request review may not be acceptable. Organizations need escape hatches for emergencies while ensuring that emergency changes are subsequently codified in Git.

State that does not fit neatly into declarative configuration challenges the GitOps model. Databases, with their persistent data, are managed differently than stateless applications. Some infrastructure components have imperative APIs that do not map cleanly to declarative resources.

Tooling maturity varies across the ecosystem. Core tools like ArgoCD and Flux are mature and widely used. Tooling for specific use cases may be less developed. Organizations may need to build custom tooling to address their specific requirements.

Despite these challenges, organizations that adopt GitOps generally find significant benefits in reliability, velocity, and auditability. The investment in declarative configuration and automation pays dividends as systems grow and change. GitOps is not a silver bullet, but it provides a coherent set of practices that align well with cloud-native infrastructure and modern development workflows.

GitOps represents a maturation of infrastructure management practices, bringing the rigor of software engineering to operations. As the tools and practices continue to evolve, GitOps is becoming the default approach for managing Kubernetes and increasingly for managing other infrastructure as well.
