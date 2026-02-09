# Component Lifecycle: UIViewController versus Activity and Fragment

The lifecycle of user interface components represents one of the starkest differences between iOS and Android development. iOS uses UIViewController with a view-driven lifecycle where the developer maintains significant control. Android uses Activity and Fragment with a system-driven lifecycle where the operating system actively manages component creation and destruction. Understanding these different philosophies is essential for effective cross-platform development.

## Philosophical Foundations of Lifecycle Design

iOS lifecycle design reflects Apple's emphasis on developer control and deterministic behavior. When you create a UIViewController, it exists until you release all references to it. The system does not spontaneously destroy your controllers. If memory becomes critically low, iOS may unload the view hierarchy to free memory, but the controller itself persists and can recreate its view when needed. This predictability enables patterns where controllers accumulate state over time, confident that state persists unless explicitly cleared.

Android lifecycle design reflects Google's emphasis on system management and resource adaptation. Activities and Fragments exist at the pleasure of the operating system. The system may destroy them when memory is needed, when configuration changes occur, or when the user navigates away. This approach enables Android to run effectively on devices with limited resources by aggressively reclaiming memory from background applications. However, it requires developers to design for destruction and recreation from the start.

These different approaches emerged from different constraints. The original iPhone had 128 megabytes of RAM and ran one foreground application at a time. iOS could assume the foreground application had adequate memory and did not need aggressive component destruction. Early Android devices had similar or less memory but needed to support multiple running applications through true multitasking. Aggressive lifecycle management enabled acceptable performance across diverse hardware with varying memory configurations.

## UIViewController Lifecycle in Detail

The UIViewController lifecycle follows a predictable sequence from initialization through deinitialization. Understanding this sequence enables placing code at the appropriate points for resource management, UI setup, and data refresh.

Initialization occurs through init methods. UIViewController can be initialized programmatically through init with nibName and bundle or through Storyboards which call init with coder. During initialization, the view does not yet exist. Properties can be initialized, dependencies injected, and instance state established, but UI configuration must wait until the view loads.

After initialization, the controller exists but its view has not been loaded. This lazy loading of views conserves memory for controllers that exist but are not yet visible. The controller remains in this state until its view property is accessed, at which point view loading begins.

View loading starts with loadView. If the controller loads from a Storyboard or NIB, the view hierarchy is inflated from that resource. If not, loadView can be overridden to create the view hierarchy programmatically. After loadView completes, the view property is no longer nil and viewDidLoad is called.

viewDidLoad is called exactly once per view load. This is the appropriate place for one-time UI setup: configuring views, establishing constraints, setting up gesture recognizers, and initializing UI state from model data. Because viewDidLoad is called only once under normal circumstances, it is appropriate for expensive setup that should not be repeated.

The view-driven lifecycle callbacks follow viewDidLoad. As the view is about to appear on screen, viewWillAppear is called. This is appropriate for updates that should occur each time the view becomes visible: refreshing data that may have changed, starting animations, updating navigation bar appearance, or subscribing to notifications.

After the view is fully visible and animation completes, viewDidAppear is called. This is appropriate for operations that should happen after the user can see the view: starting resource-intensive work, triggering analytics for screen views, or showing dialogs that should appear after navigation completes.

The disappearance callbacks mirror appearance. viewWillDisappear is called as the view is about to leave the screen, appropriate for saving draft data, stopping animations, and unsubscribing from notifications. viewDidDisappear is called after the view is no longer visible, appropriate for stopping resource-intensive operations and releasing resources not needed while hidden.

Deinitialization occurs when the last strong reference to the controller is released. The deinit method is called, providing a final cleanup opportunity. This is appropriate for removing notification observers, canceling pending operations, and releasing resources. Because ARC ensures deinit is called deterministically when the reference count reaches zero, cleanup code in deinit executes reliably.

## Activity Lifecycle in Detail

The Activity lifecycle is more complex than UIViewController because it must accommodate system-driven destruction and recreation. Activities can be destroyed for memory pressure, configuration changes, or normal navigation, and must handle each case appropriately.

Activity creation begins with onCreate. The system passes a Bundle parameter that is null for first creation and contains saved state for recreation after destruction. This single callback handles both cases, with code checking for null to distinguish them. During onCreate, the Activity should restore state from the Bundle if present, set the content view, and perform initialization that should happen once per creation.

Unlike iOS where viewDidLoad happens once per controller lifetime, Android onCreate happens each time the Activity is created, which may be multiple times in its conceptual lifetime. A screen rotation destroys and recreates the Activity, calling onCreate again. Code that assumes onCreate runs once will behave incorrectly after configuration changes.

After onCreate, the Activity becomes visible through onStart. This corresponds roughly to iOS viewWillAppear. The Activity is now visible to the user but may not be in the foreground receiving input. This is appropriate for operations that should happen while the Activity is visible regardless of whether it has focus.

After onStart, the Activity gains focus through onResume. This is the running state where the Activity is fully visible, has focus, and receives input. Most activities spend most of their time in this state. This is appropriate for starting animations, enabling input, and any other operations that should occur only while the Activity is actively used.

When the Activity loses focus but remains visible, onPause is called. This happens when a dialog appears, when entering multi-window mode with another window focused, or during navigation away. This callback must complete quickly because the next Activity cannot appear until onPause returns. Save critical state here, but defer expensive operations.

When the Activity is no longer visible, onStop is called. This is appropriate for more expensive cleanup and state saving. Unlike onPause which must be fast, onStop has more time available. Resources that should not be held while invisible should be released here.

The critical callback for surviving destruction is onSaveInstanceState. This is called before the Activity may be destroyed, providing an opportunity to save state that should survive recreation. The state is passed to onCreate when the Activity is recreated. This mechanism enables activities to maintain user-visible state across destruction and recreation.

After onStop, the Activity may be destroyed through onDestroy or may return to visibility through onRestart followed by onStart. onDestroy is called when the Activity is being removed from memory, either because finish was called or because the system needs to reclaim resources. However, onDestroy is not guaranteed to be called, especially during system-initiated destruction. Critical cleanup should not depend on onDestroy running.

## Fragment Lifecycle Complexity

Fragments add another layer of lifecycle complexity on Android. Originally introduced to enable tablet layouts with multiple panes, Fragments have become the standard building block for Android UI composition. However, their lifecycle is notoriously complex because it interweaves with the host Activity lifecycle.

Fragments have their own lifecycle callbacks that parallel Activity callbacks: onCreate, onCreateView, onViewCreated, onStart, onResume, onPause, onStop, onDestroyView, and onDestroy. These callbacks occur within the context of the host Activity's lifecycle, creating numerous possible state combinations.

The Fragment view lifecycle is distinct from the Fragment instance lifecycle. A Fragment can exist without a view, can have its view destroyed while the Fragment persists, and can have its view recreated later. This happens when fragments are on a back stack with their views destroyed to conserve memory but their instances retained for state preservation.

This separation of view and instance lifecycle creates the need for viewLifecycleOwner in Fragments. UI-related operations should be scoped to the view lifecycle, not the Fragment lifecycle, because the view may not exist when the Fragment does. Observing data to update UI should use viewLifecycleOwner to ensure observation stops when the view is destroyed, even if the Fragment continues to exist.

The Fragment lifecycle adds callbacks not present in Activity lifecycle. onAttach is called when the Fragment is associated with its host Activity. onCreateView creates the Fragment's view hierarchy, corresponding to UIViewController's loadView. onViewCreated is called after the view hierarchy is created, corresponding to viewDidLoad. onDestroyView destroys the view while potentially retaining the Fragment instance. onDetach removes the Fragment from its host.

Fragment transactions and the back stack further complicate lifecycle management. Adding a Fragment to the back stack means its view is destroyed when navigating away but its instance is retained. Navigating back recreates the view with a new onCreateView and onViewCreated, but not onCreate since the instance persisted. State in the view is lost, but state in the Fragment instance survives.

## Configuration Changes and Recreation

Configuration changes on Android trigger Activity and Fragment destruction and recreation by default. Screen rotation, keyboard attachment, language change, and other configuration modifications destroy the current instances and create new ones. This behavior enables the system to load appropriate resources for the new configuration but requires developers to handle state preservation.

The Bundle mechanism handles primitive state preservation. onSaveInstanceState receives a Bundle where state can be stored. onCreate receives a Bundle containing the saved state. This works well for small amounts of data but has limitations: the Bundle should remain small because it is serialized to disk, and not all data types can be stored directly.

ViewModel addresses the limitations of Bundle state preservation. ViewModels are retained across configuration changes, surviving Activity recreation. They can hold any data type without serialization concerns. They are scoped to lifecycle owners, typically Activities or Fragments, and are cleared when the scope is permanently finished rather than temporarily destroyed.

iOS has no equivalent to configuration change recreation. Screen rotation does not destroy view controllers. Trait collection changes notify controllers but do not recreate them. Controllers can respond to size class changes by adjusting their layout but maintain continuous existence throughout. This simplifies state management because state does not need to survive recreation.

Porting code that assumes iOS continuous existence to Android requires adding state preservation. Every piece of state that should survive rotation must be either saved to a Bundle or held in a ViewModel. Porting code that assumes Android recreation to iOS requires recognizing that state preservation code may be unnecessary since recreation does not occur.

For cross-platform code, the safest assumption is that state may need to be preserved and restored. Even though iOS does not require it for configuration changes, designing code that cleanly separates state from presentation benefits both platforms.

## Process Death and Restoration

Beyond configuration changes, Android applications face process death. The operating system may kill application processes to reclaim memory, with no guarantee that the process will complete any particular lifecycle callback before death. When the user returns to the application, it is launched fresh but should restore to its previous state as if nothing happened.

The Bundle mechanism extends to process death restoration. State saved in onSaveInstanceState survives process death because it is persisted to disk. When the application relaunches, the system recreates the Activity stack and passes saved Bundles to each Activity's onCreate. Properly implemented state preservation creates seamless restoration.

ViewModels do not survive process death because they are in-memory objects. SavedStateHandle provides ViewModel-compatible state preservation that does survive process death. SavedStateHandle wraps Bundle access in a ViewModel-friendly API, enabling ViewModels to participate in cross-process-death state preservation.

iOS has a similar concept but different implementation. The jetsam system may terminate applications to reclaim memory, but there is no automatic state restoration mechanism equivalent to Android's Bundle. Applications can implement state preservation through NSCoding and restoration identifiers, but this is opt-in and less commonly used than Android's mandatory state preservation patterns.

Porting Android code that relies on automatic state restoration to iOS requires implementing equivalent preservation manually or accepting that state may be lost on termination. Porting iOS code that does not handle termination restoration to Android requires adding Bundle state preservation to maintain Android user expectations.

Cross-platform code should assume process death can occur at any time. Critical state should be persisted to disk, not just held in memory. Shared business logic should support serialization of its state. Platform-specific code should use platform mechanisms to persist and restore that state.

## Lifecycle-Aware Components

Both platforms have evolved toward lifecycle-aware components that automatically manage their own lifecycle based on their host's lifecycle. This reduces boilerplate code and eliminates errors from forgetting to start or stop components at appropriate lifecycle points.

Android's Lifecycle library provides lifecycle-aware components through the LifecycleObserver interface. Components implement lifecycle callbacks and register with a lifecycle owner. When the owner's lifecycle changes, observers are notified automatically. This enables patterns where components like location managers or network monitors start and stop themselves based on the host Activity or Fragment lifecycle.

LiveData extends lifecycle awareness to data observation. Observers registered with a lifecycle owner automatically receive updates only when the owner is active and automatically unregister when the owner is destroyed. This prevents common bugs where observers continue receiving updates after their host is destroyed.

iOS has developed similar patterns though less systematically. Combine subscriptions can be stored in cancellable collections that cancel subscriptions when deallocated. SwiftUI views automatically manage subscriptions to ObservableObjects. UIKit components can use notification observers that are removed in deinit.

For cross-platform development, Kotlin coroutines and Flow provide lifecycle-aware patterns. CoroutineScope can be scoped to lifecycle, with coroutines automatically canceled when the scope ends. Flow collection can be scoped similarly. These patterns work on both platforms when appropriately integrated with platform lifecycle mechanisms.

## Practical Implications for Cross-Platform Development

The lifecycle differences between platforms have profound implications for cross-platform architecture. Shared code must not assume either platform's lifecycle behavior. Business logic that works under iOS continuous existence might fail under Android recreation. Business logic that relies on Android state preservation callbacks might lack equivalent iOS integration points.

The safest approach is to isolate state in platform-agnostic structures that can be serialized and restored. Shared ViewModels or state holders should expose their state in serializable form. Platform-specific code handles the mechanics of saving and restoring that state using platform mechanisms.

Navigation state requires particular attention. iOS navigation controllers maintain their stack continuously. Android navigation components must restore their stack from saved state after recreation. Cross-platform navigation solutions like Decompose handle this by maintaining serializable navigation state that platforms can persist and restore.

Asynchronous operations must handle lifecycle interruption. An operation started before configuration change might complete after recreation. On Android, the original Activity that started the operation no longer exists; the operation must somehow deliver its result to the new Activity. Shared patterns like delivering results through ViewModels or reactive streams that are recreated and reconnected handle this gracefully.

Testing should verify behavior under both lifecycle models. Tests that create components, simulate lifecycle events, and verify correct behavior should run on both platforms. Android tests should include configuration change simulation to verify state preservation. iOS tests should verify correct behavior through normal lifecycle transitions.

## Conclusion

The lifecycle models of iOS and Android reflect their different design philosophies. iOS provides predictable, developer-controlled lifecycles that simplify state management but provide less system flexibility. Android provides system-managed lifecycles that enable resource adaptation but require careful state preservation.

Effective cross-platform developers understand both models deeply. They recognize that iOS view controllers persist while Android activities may be recreated. They design shared state management that works under both assumptions. They test on both platforms to catch lifecycle-related bugs that manifest differently on each.

The evolution of both platforms toward lifecycle-aware components shows convergence in recognizing the importance of automatic lifecycle management. Modern patterns on both platforms reduce manual lifecycle handling, though the underlying models remain distinct. Cross-platform code can leverage these patterns while respecting the fundamental differences in how each platform manages component lifecycles.
