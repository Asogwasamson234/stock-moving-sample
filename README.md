# Stock Moving Sample: **High-Performance Visual Pipeline**

This project is a high-performance framework demonstrating real-time quantitative chart tracking inside Python using
matplotlib. It models an algorithmic trading interface that tracks an asset's price, calculates double-exponential
mathematical indicators concurrently, and renders technical crossover signals without frame latency.

## Architecture & System Flow

The script uses a decoupled architecture separating data collection from UI rendering. This approach ensures that data
collection does not cause interface lockups or performance bottlenecks.

```
+------------------------+      Price Ticks      +----------------------------+
|  StockDataStream       | --------------------> |    FuncAnimation Update    |
| (Memory Buffer & EMAs) |                       | (Handles Viewport Shifts)  |
+------------------------+                       +----------------------------+
                                                               |
                                                               v
                                                 +----------------------------+
                                                 | Optimized Rendering Canvas |
                                                 | (Direct Object Mutators)   |
                                                 +----------------------------+
```

## Advanced Optimization Engineering

Standard plotting workflows often become unstable when running animations over long

durations. This project overcomes those limitations using four specific engineering approaches:

- **Deterministic Memory Boundaries via Deque:** Standard Python `list` types grow indefinitely, which triggers garbage
  collection cycles and
  memory
  fragmentation during continuous data collection. This framework uses `collections.deque(maxlen=150)`. When the array
  hits
  its **151st** data point, index **0** is safely purged in an **$O(1)$** operation, locking the system’s memory
  overhead down
  to a
  flat profile.


- **In-Place Resource Recycling (`set_data` over `plot`):** Calling functions like `plt.plot() or ax.scatter()`
  repeatedly forces `matplotlib` to instantiate entirely new geometric objects inside the memory tree every frame. This
  script builds three persistent object pointers **$(line_price, line_fast, line_slow)$** once at startup. Every 40ms,
  the
  engine simply shifts the raw numeric arrays inside those existing lines using $`.set_data()`$.


- **Dynamic Viewport Domain Bounds:** Unlike static streaming plots with fixed windows, this engine calculates
  structural
  data boundaries on the fly.
  As the timeline ticks forward, the horizontal grid automatically tracks the latest 150 points (`ax.set_xlim`).
  Concurrently, the vertical grid samples the historical min/max values inside the active queue buffer, adding a
  responsive 15% baseline boundary cushion (`ax.set_ylim`).


- **Transient Collection Management:** When a **"Golden Cross"** or **"
  Death Cross"** event occurs, temporary scatter vectors are drawn onto the coordinate grid. To avoid accumulating old
  visual
  artifacts in memory, these objects are appended to a tracking list (`scatter_markers`) and explicitly explicitly
  cleared
  out of the axes memory buffer using `.remove()` before drawing the next frame

## **Customization & Extension Guide**

- **Hooking up Live APIs:** To stream real-world equities or crypto markets, replace the

contents of the `generate_next_tick` method with
an API hook or web socket connector (e.g., `requests.get()` from Binance or Alpaca) that updates
`self.current_price`.

- **Tweaking Indicator Speeds:** Adjust `FAST_ALPHA` and `SLOW_ALPHA`. The closer alpha is to **1.0**, the more
  responsive the lines become to instant price changes. Lower alpha values smooth out volatility over a broader time
  horizon.