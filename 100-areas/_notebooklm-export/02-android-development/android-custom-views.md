# Android Custom Views: Canvas, Paint, and Touch Handling

Custom views represent the most fundamental way to create unique visual components on Android. When standard widgets cannot express your design vision or interaction model, custom views provide complete control over drawing, measurement, and user interaction. Understanding custom view development requires mastery of the Canvas drawing API, the Paint configuration system, and touch event handling. These systems form the foundation upon which all Android UI ultimately rests.

The decision to create a custom view should come after considering alternatives. Standard views with styling modifications often suffice. Drawable resources can create complex visual effects without custom view code. Compound views that combine existing views provide reuse without custom drawing. But when you need pixel-perfect control over appearance or novel interaction patterns, custom view implementation becomes the appropriate tool.

## The Canvas Abstraction

Canvas provides the surface for all drawing operations in Android views. When your custom view's onDraw method receives a Canvas parameter, that canvas represents the rectangular drawing area where your view's visual content will appear. The canvas handles transformation, clipping, and command recording, presenting a coherent drawing abstraction regardless of the underlying rendering mechanism.

The coordinate system of a Canvas places the origin at the upper left corner of the drawing area, with x increasing rightward and y increasing downward. This convention matches screen coordinate systems but differs from mathematical conventions where y increases upward. Drawing coordinates use pixels, though the framework may scale for display density when hardware acceleration applies.

Canvas provides methods for drawing primitives, text, bitmaps, and paths. The drawRect method fills or strokes rectangles given coordinates or a Rect object. The drawCircle method draws circles given center coordinates and radius. The drawOval method draws ellipses within bounding rectangles. The drawLine method draws line segments between point pairs. The drawArc method draws partial circles or ellipses specified by angles.

Text drawing uses drawText and related methods. Text positions by the baseline of the first character, not the upper left corner of the text bounds. This baseline positioning matches typography conventions but requires adjustment when aligning text with other elements. The Paint object specifies font, size, and text alignment properties.

Bitmap drawing uses drawBitmap methods with various signatures for different use cases. Simple cases place a bitmap at specified coordinates. Transformation cases map source rectangles to destination rectangles with scaling. Matrix cases apply arbitrary transformations. All cases respect the Paint's alpha and color filter settings.

Path drawing uses drawPath to render arbitrary shapes defined by Path objects. Paths contain sequences of lines, curves, and shape operations. Complex custom shapes that cannot be expressed as single primitives use Path construction followed by drawPath rendering.

## Paint Configuration

The Paint class configures how drawing operations render. Every canvas drawing method that produces visible output takes a Paint parameter. The separation between what to draw (Canvas methods) and how to draw (Paint configuration) enables flexible reuse. The same Paint can render multiple shapes; the same shape can render with different Paints.

Color configuration sets the primary drawing color through setColor or setARGB. The color applies to filled shapes, stroked shapes, and text. Alpha channel values enable transparency effects; a zero alpha makes drawing invisible while full alpha makes it opaque.

Style configuration determines whether shapes render filled, stroked, or both. The FILL style fills the interior of shapes with solid color. The STROKE style draws the outline of shapes without filling. The FILL_AND_STROKE style does both, with the stroke extending outward from the shape boundary.

Stroke configuration controls stroke appearance when style includes stroking. The strokeWidth property sets the line thickness in pixels. The strokeCap property determines how line ends appear: BUTT cuts off flat, ROUND adds semicircular caps, SQUARE adds square caps extending past the endpoint. The strokeJoin property determines how connected line segments meet: MITER creates pointed corners, ROUND creates curved corners, BEVEL creates cut corners.

Text configuration controls typography when drawing text. The textSize property sets the font size in pixels. The typeface property sets the font family and weight. The textAlign property controls how text positions relative to the specified coordinate: LEFT starts text at the coordinate, CENTER centers text on the coordinate, RIGHT ends text at the coordinate.

Anti-aliasing smooths the edges of drawn shapes by blending edge pixels with the background. The isAntiAlias property enables this smoothing. Without anti-aliasing, diagonal lines and curves show visible staircasing artifacts. With anti-aliasing, edges appear smooth but draw slightly slower. Most drawing benefits from anti-aliasing.

The flags passed to the Paint constructor provide convenient initialization. The ANTI_ALIAS_FLAG enables anti-aliasing from construction. Constructing with Paint(Paint.ANTI_ALIAS_FLAG) is more concise than constructing then calling setAntiAlias(true) separately.

## Shaders for Advanced Fill Patterns

Shaders extend fill patterns beyond solid colors. When a Paint has a shader set, the shader determines pixel colors instead of the simple color property. Shaders enable gradients, patterns, and image-based fills that would be impossible with solid colors alone.

LinearGradient creates a gradient that transitions between colors along a line. You specify start and end points defining the gradient direction, colors at each position, and optionally intermediate color stops. The gradient interpolates between colors based on position along the gradient line. TileMode controls behavior outside the gradient line: CLAMP extends edge colors, REPEAT tiles the gradient, MIRROR reflects alternating tiles.

RadialGradient creates a gradient that radiates from a center point. You specify the center coordinates, the radius at which the gradient ends, and the color configuration. Colors transition from center to edge based on distance from the center point.

SweepGradient creates a gradient that sweeps around a center point like a radar sweep. Colors transition based on angle rather than distance. The gradient completes one full cycle around the center.

BitmapShader fills shapes with a tiled or stretched bitmap image. You specify the source bitmap and tile modes for each axis. Common uses include circular image cropping where you draw a circle with a BitmapShader containing the image, producing a circular crop without actual image manipulation.

ComposeShader combines two shaders using Porter-Duff composition modes. This enables complex effects like gradient-masked patterns or combined linear and radial gradients.

## Porter-Duff Composition

Porter-Duff composition modes control how newly drawn pixels combine with existing pixels. The PorterDuff.Mode enumeration defines the standard composition operations. These operations consider source and destination pixels, each with color and alpha channels, and produce output pixels according to mathematical formulas.

The SRC mode replaces destination with source completely. The DST mode keeps destination, ignoring source. The SRC_OVER mode places source over destination with alpha blending, the default behavior for most drawing.

The SRC_IN mode shows source only where destination exists. This enables masking effects where a shape drawn first limits where subsequent drawing appears. The DST_IN mode is the inverse, showing destination only where source exists.

The SRC_OUT mode shows source only where destination does not exist. The DST_OUT mode shows destination only where source does not exist. These modes enable hole-punching effects.

The XOR mode shows source and destination where they do not overlap, with neither showing where they do overlap. The CLEAR mode makes pixels transparent regardless of source and destination values.

Applying Porter-Duff modes uses the setXfermode method on Paint with a PorterDuffXfermode object. The mode affects subsequent drawing operations until changed. Complex compositions often require drawing to off-screen bitmaps or using saveLayer to isolate composition from the underlying canvas.

The saveLayer method creates an off-screen buffer for subsequent drawing. Drawing after saveLayer goes to the buffer rather than directly to the canvas. The restore method composites the buffer onto the canvas. This isolation enables Porter-Duff operations that would not work correctly when drawing directly onto existing content.

## Path Construction

Path objects define complex shapes through sequences of drawing commands. The path abstraction enables shapes far more complex than the primitive methods support directly. A Path accumulates commands until drawing renders the complete shape.

Movement commands position the current point without drawing. The moveTo method moves to absolute coordinates. The rMoveTo method moves relative to the current point. These commands start new subpaths within the overall path.

Line commands draw straight segments. The lineTo method draws to absolute coordinates. The rLineTo method draws to relative coordinates. These commands extend the current subpath with line segments.

Curve commands draw curved segments. The quadTo method draws quadratic Bezier curves with one control point. The cubicTo method draws cubic Bezier curves with two control points. These curves enable smooth, organic shapes that straight lines cannot achieve.

The close method completes a subpath by drawing a line from the current point to the subpath's starting point. Closed paths create bounded regions that can be filled. Unclosed paths still render their segments but do not enclose area.

Shape convenience methods add complete shapes to the path. The addRect, addCircle, addOval, and addRoundRect methods add their respective shapes. The direction parameter controls whether the shape adds clockwise or counterclockwise, affecting fill rule behavior.

The setFillType method controls how overlapping path regions fill. WINDING fills areas enclosed by the path considering direction. EVEN_ODD fills areas enclosed an odd number of times regardless of direction. These rules determine appearance when paths cross themselves.

## Implementing onDraw

The onDraw method is where custom view drawing logic lives. The framework calls onDraw when the view needs to render its content, passing a Canvas configured for the view's bounds. Your implementation uses Canvas drawing methods to produce the view's visual appearance.

The cardinal rule of onDraw implementation is avoiding object allocation. The onDraw method can be called many times per second during animations and scrolling. Each allocation during onDraw creates garbage that eventually requires collection, causing frame drops and visual stuttering. Create Paint, Path, Rect, and other objects as instance fields initialized once, not as local variables in onDraw.

Paint objects should be created in the constructor or init block and configured once. If properties change dynamically, update the existing Paint rather than creating a new one. Store Paint objects as private fields with appropriate names indicating their purpose.

Path objects often need updating when view size changes or content changes. Create the Path as an instance field, then call reset() and rebuild the path in onSizeChanged when dimensions change. This avoids allocation in onDraw while keeping path data current.

Rect and RectF objects for bounds calculations should also be instance fields. Update their values in onDraw using set() rather than creating new instances. The temporary nature of these calculations does not justify the allocation overhead.

The onSizeChanged callback provides an appropriate place for size-dependent calculations. When the view receives its first size or when its size changes, onSizeChanged fires with old and new dimensions. Calculate radii, centers, path definitions, and other geometry here, storing results in instance fields for onDraw to use.

## Measurement Implementation

Custom views participate in the Android layout system through measurement. The onMeasure method receives constraints from the parent view and must determine the view's desired size. Proper measurement ensures your custom view works correctly in various container contexts.

MeasureSpec encodes both a size constraint and a constraint mode. The EXACTLY mode indicates the parent has determined a specific size the view must use. The AT_MOST mode indicates a maximum size the view can use. The UNSPECIFIED mode indicates no constraint, typically within scrollable containers.

Extracting mode and size uses MeasureSpec.getMode and MeasureSpec.getSize. These methods decode the integer measureSpec into its components. Your onMeasure implementation examines these values to determine behavior.

Typical onMeasure implementations calculate a desired size based on content, then reconcile that desire with the constraints. For EXACTLY mode, use the specified size. For AT_MOST mode, use the minimum of desired and specified. For UNSPECIFIED mode, use the desired size. The resolveSize helper method performs this reconciliation automatically.

The setMeasuredDimension method must be called before onMeasure returns. This method records the view's measured width and height. Failing to call it throws an exception. The values passed become available through getMeasuredWidth and getMeasuredHeight for subsequent layout calculations.

For views that should be square, take the minimum of width and height constraints and apply it to both dimensions. For views with aspect ratios, calculate one dimension from the other based on the constraint modes. For views with minimum sizes, ensure the measured dimensions meet minimums regardless of constraints.

## Touch Event Fundamentals

Touch handling transforms your custom view from a static image into an interactive component. The Android touch system delivers touch events through callback methods that your view overrides. Understanding the touch event model is essential for creating intuitive interactive behavior.

MotionEvent objects describe touch state at a moment in time. The event contains the touch position, the action that occurred, and additional information like pressure and contact size. Different actions represent different phases of the touch interaction.

The ACTION_DOWN action indicates the first finger touching the screen. This action begins a gesture and represents an opportunity to claim the gesture for your view. Your onTouchEvent should return true for ACTION_DOWN if it wants to handle the gesture, claiming subsequent events in the sequence.

The ACTION_MOVE action indicates finger movement while in contact with the screen. Multiple moves may occur between down and up actions. Your handling tracks position changes to implement drag, scroll, or drawing behavior.

The ACTION_UP action indicates the last finger lifting from the screen. This action ends the gesture. Your handling typically performs final operations like launching a click callback or completing an animation.

The ACTION_CANCEL action indicates the gesture has been terminated by the system or a parent view. When a parent intercepts the gesture, the child receives ACTION_CANCEL instead of ACTION_UP. Your handling should treat cancellation like completion, cleaning up any gesture-specific state.

The boolean return value from onTouchEvent is critical. Returning true indicates you handled the event and want subsequent events in the gesture. Returning false indicates you did not handle it, and the event should propagate to parent views. Crucially, returning false for ACTION_DOWN means you will not receive subsequent events in that gesture at all.

## Implementing Interactive Behavior

Drag interactions track finger position and update view state accordingly. On ACTION_DOWN, record the initial touch position and any initial state you need to preserve. On ACTION_MOVE, calculate the delta from the initial position or from the last position and update state. On ACTION_UP or ACTION_CANCEL, finalize the interaction.

Touch slop represents the minimum finger movement before recognizing a drag gesture. Small finger movements, even when attempting to tap, produce slightly different positions between down and up events. The ViewConfiguration class provides scaledTouchSlop, the system's recommended minimum drag distance. Compare movement against touch slop before beginning drag behavior.

Velocity tracking enables fling gestures that continue after the finger lifts. The VelocityTracker class accumulates position samples and computes velocity. Create or obtain a VelocityTracker on ACTION_DOWN, add each event with addMovement, compute velocity before ACTION_UP with computeCurrentVelocity, and retrieve velocity values. Recycle the tracker after use.

Click recognition requires distinguishing taps from drags. A tap occurs when the finger lifts without exceeding touch slop. Track movement distance and only fire click behavior if movement stays within the threshold. The performClick method handles accessibility requirements and should be called for all clicks.

Long press recognition requires detecting extended touch duration without movement. The Handler class can post delayed runnables that fire if not canceled. Schedule a long press runnable on ACTION_DOWN, cancel it on significant movement or on UP, and fire long press behavior if the runnable executes.

## Multi-Touch Handling

Multi-touch interactions involve multiple fingers simultaneously, enabling gestures like pinch-to-zoom and rotation. The touch event model extends to support multiple pointers with careful attention to pointer identity and indexing.

Pointer index identifies a finger within a single MotionEvent's arrays. The index might be 0, 1, 2, and so on depending on how many fingers are down. However, pointer indices can change between events as fingers lift. The first finger might be index 0 in one event and index 0 in the next, or index 0 might represent a different finger if the original first finger lifted.

Pointer ID provides stable identification across events. Each finger receives an ID when it touches down that remains constant until that finger lifts. Use getPointerId to get the ID for an index, and findPointerIndex to find the current index for a known ID. Tracking by ID ensures you follow the correct finger through the gesture.

ACTION_POINTER_DOWN and ACTION_POINTER_UP indicate secondary fingers touching or lifting. The primary finger uses ACTION_DOWN and ACTION_UP, but additional fingers use the POINTER variants. The action index, retrieved through getActionIndex, indicates which pointer the action applies to.

The actionMasked property isolates the action type from the action index. Using getActionMasked with when-expressions handles all action types cleanly. Raw action values include encoded indices that complicate equality checking.

Scale gesture detection for pinch-to-zoom uses the ScaleGestureDetector class. Create a detector with a listener, pass all touch events to it via onTouchEvent, and handle scale callbacks in the listener. The detector handles the geometry of tracking two fingers and computing scale factors.

## Gesture Detection

The GestureDetector class simplifies recognition of common gestures. Rather than implementing gesture recognition logic yourself, you create a detector with a listener and feed it touch events. The detector invokes listener callbacks for recognized gestures.

Creating a GestureDetector requires a context and a listener. The SimpleOnGestureListener class provides default implementations for all callbacks, allowing you to override only those you care about. The onDown callback should return true to indicate interest in the gesture.

The onSingleTapConfirmed callback fires for single taps after ensuring it is not a double tap. The onDoubleTap callback fires for the second tap of a double tap. These callbacks provide clean separation of single and double tap behavior.

The onScroll callback fires during drag gestures, providing the start event, current event, and distance traveled since the last callback. Note that distance values represent motion since the previous callback, not since the gesture start. Accumulate values if you need total displacement.

The onFling callback fires when a drag gesture ends with velocity, providing both the start and end events and the velocity in both axes. Velocity values are in pixels per second. Use these values to animate continued motion after the finger lifts.

The onLongPress callback fires when a touch is held without movement. Unlike the other callbacks, onLongPress is void rather than boolean because by the time it fires, the gesture is already committed.

## Combining Detectors with Custom Logic

Real-world custom views often need gesture detection alongside custom touch handling. The pattern involves passing events to detectors first, then handling events yourself if the detectors did not consume them.

Create detectors in the view constructor and store them as instance fields. In onTouchEvent, pass the event to each detector. If all detectors return false, perform your own handling. Return true if any handling consumed the event.

Some interactions require knowing gesture state that detectors do not expose. Track your own state alongside detector use. For example, track whether a scale gesture is in progress to disable single-finger panning during pinch-to-zoom.

Detectors that handle events but do not consume them present coordination challenges. The GestureDetector's onDown returns true to claim the gesture, but you might also need ACTION_DOWN handling. Structure your code so detector callbacks and direct event handling can coexist.

## Accessibility for Custom Views

Custom views require explicit accessibility implementation. Standard widgets provide accessibility automatically, but custom drawing and interaction need manual accessibility support.

Content description provides a text description that screen readers announce. For simple custom views, setting a content description through setContentDescription conveys what the view represents. Update the description when the view's represented value changes.

Accessibility actions enable screen reader users to interact with the view. Override performAccessibilityAction to handle action requests. Return true if you handled the action. Standard actions like ACTION_CLICK and ACTION_LONG_CLICK have predefined IDs. Custom actions can be added through AccessibilityNodeInfo.

The AccessibilityNodeInfo object describes your view to accessibility services. Override onInitializeAccessibilityNodeInfo to populate the node with information. Set the class name to indicate what standard control your view resembles. Add action availability. Set state information like checked or selected.

Live regions announce changes to screen readers automatically. Set accessibilityLiveRegion on views whose content changes dynamically. The POLITE setting queues announcements. The ASSERTIVE setting interrupts current speech for immediate announcement.

For complex custom views with multiple interactive regions, consider implementing AccessibilityDelegate or using multiple views. A single custom view can only have one accessibility focus point, which may be insufficient for complex controls.

## Performance Optimization

Custom view performance affects application responsiveness. Several optimization techniques ensure your custom views render efficiently.

Avoid allocations in onDraw as discussed earlier. Also avoid allocations in onTouchEvent, onMeasure, and other frequently called methods. Profile memory allocations using Android Studio's profiler to identify unexpected allocations.

Hardware layers cache view content as GPU textures. For views that animate without internal content changes, enable a hardware layer before the animation and disable it after. The withLayer method on ViewPropertyAnimator handles this automatically for property animations.

Clip rect optimization limits drawing to only the visible region. If you know portions of your view are outside the visible area, use canvas.quickReject to check whether rectangles intersect the visible region before drawing. Skip drawing for rejected rectangles.

Invalidation precision requests redrawing only the affected region. The invalidate method accepts a dirty rectangle. If only part of your view changed, invalidate only that part. The system may still redraw more, but providing hints enables optimization.

Bitmap handling significantly impacts performance. Large bitmaps consume memory and slow rendering. Load bitmaps at the size you actually need using BitmapFactory.Options with inSampleSize. Consider bitmap caching strategies for bitmaps that change infrequently.

## State Preservation

Custom views that maintain state should save and restore that state across configuration changes and process death. The framework provides hooks for state preservation that custom views must implement.

The onSaveInstanceState method returns a Parcelable containing state to preserve. Create a custom Parcelable subclass that stores your view's state. Call the superclass method first and pass its result to your Parcelable constructor to chain state correctly.

The onRestoreInstanceState method receives the Parcelable returned earlier. Cast to your custom Parcelable type, extract preserved values, and apply them to the view. Call the superclass method with the base state your Parcelable chained.

State saving only works for views with IDs. The framework uses view ID as the key for state storage. Views without IDs cannot participate in automatic state saving. Always assign IDs to custom views that have saveable state.

The BaseSavedState class provides a convenient base for custom state Parcelables. Extend BaseSavedState, add fields for your state, implement the writeToParcel and constructor-from-Parcel methods, and provide a CREATOR constant. This structure ensures proper state chaining.

## Testing Custom Views

Custom view testing verifies both visual output and interaction behavior. Different testing approaches address different aspects.

Unit tests verify logic extracted from view methods. Calculations for positions, colors, or other values can be tested directly if factored into pure functions. This testing does not require instrumentation.

Instrumented tests run on devices or emulators with access to the Android framework. You can create custom view instances, call methods, and verify resulting state. The onDraw method can be tested by providing a mock Canvas or by capturing rendered output.

Screenshot testing captures view rendering and compares against reference images. This approach catches visual regressions that unit tests miss. Several libraries provide screenshot testing capabilities with difference highlighting.

Touch interaction testing simulates touch events and verifies resulting behavior. The Espresso framework can perform actions on views, but custom gestures may require injecting MotionEvents directly. Verify state changes, callback invocations, and visual updates result from simulated interaction.

Accessibility testing verifies screen reader compatibility. The Accessibility Scanner tool identifies common issues. Automated tests can verify content descriptions and action availability. Manual testing with TalkBack reveals real-world screen reader experience.

## Compose Canvas Integration

Compose provides its own Canvas composable for custom drawing that integrates with the Compose state and layout systems. Understanding how Compose Canvas relates to View Canvas helps when working with both systems.

The Canvas composable receives a modifier and a drawing lambda. The lambda receives a DrawScope that provides drawing methods similar to android.graphics.Canvas. The DrawScope methods use Compose types like Color and Size rather than Android graphics types.

State observation works automatically in Canvas drawing lambdas. Reading Compose state within the lambda causes redrawing when that state changes. This integration means you do not need explicit invalidation calls. Just read state, and updates happen automatically.

Modifiers on Canvas composables affect size, padding, and clipping just like other composables. The Canvas composable does not have intrinsic size, so you must specify size through modifiers or containing layout constraints.

Touch handling in Compose uses the pointerInput modifier rather than onTouchEvent overrides. The modifier provides suspend functions for detecting various gestures. State from pointer input can flow to Canvas drawing through normal state mechanisms.

Converting between View Canvas and Compose Canvas patterns involves understanding the conceptual similarities and syntactic differences. The drawing primitives are equivalent. The state management differs. Migration can be straightforward if drawing logic is properly factored from state and measurement logic.
