from collections import deque

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

# ==============================================================================
# CONFIGURATION & PARAMETERS
# ==============================================================================
WINDOW_SIZE = 150  # Number of visible ticks on the screen at one time
FAST_ALPHA = 0.1  # Smoothing factor for the Fast EMA (~19-period equivalent)
SLOW_ALPHA = 0.03  # Smoothing factor for the Slow EMA (~65-period equivalent)
UPDATE_INTERVAL = 40  # Screen update interval in milliseconds (~25 Frames Per Second)


# ==============================================================================
# OBJECT-ORIENTED DATA FEED MANAGER
# ==============================================================================
class StockDataStream:
    """
    Manages high-performance real-time calculation and streaming of asset prices
    and their corresponding Exponential Moving Averages (EMA).
    """

    def __init__(self, max_len=WINDOW_SIZE, fast_alpha=FAST_ALPHA, slow_alpha=SLOW_ALPHA):
        # deques maintain a strict memory limit; older points drop automatically
        self.time_steps = deque(maxlen=max_len)
        self.prices = deque(maxlen=max_len)
        self.fast_ema = deque(maxlen=max_len)
        self.slow_ema = deque(maxlen=max_len)

        # State tracking for statistical calculations
        self.current_price = 100.0  # Initial asset base price
        self.last_fast = 100.0
        self.last_slow = 100.0
        self.fast_alpha = fast_alpha
        self.slow_alpha = slow_alpha

    def generate_next_tick(self, frame):
        """Simulates a stock price tick using a Random Walk with a slight upward drift."""
        # Random percentage change between -1.2% and +1.3%
        pct_change = np.random.uniform(-0.012, 0.013)
        self.current_price *= (1.0 + pct_change)

        # Calculate EMA values using the recurrence formula: EMA_today = (Price_today * alpha) + (EMA_yesterday * (1 - alpha))
        if frame == 0:
            f_ema = self.current_price
            s_ema = self.current_price
        else:
            f_ema = (self.current_price * self.fast_alpha) + (self.last_fast * (1.0 - self.fast_alpha))
            s_ema = (self.current_price * self.slow_alpha) + (self.last_slow * (1.0 - self.slow_alpha))

        # Update historical state markers
        self.last_fast = f_ema
        self.last_slow = s_ema

        # Append to the performance-optimized queues
        self.time_steps.append(frame)
        self.prices.append(self.current_price)
        self.fast_ema.append(f_ema)
        self.slow_ema.append(s_ema)


# ==============================================================================
# VISUALIZATION INITIALIZATION
# ==============================================================================
# Instantiate data engine
stream = StockDataStream()

# Setup professional canvas styling
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(12, 6))
fig.canvas.manager.set_window_title('Stock Moving Sample - Real-Time Dashboard')

# Set up static text and axis bounds
ax.set_title('Real-Time Stock Stream & Dual EMA Engine', fontsize=14, fontweight='bold', pad=15)
ax.set_ylabel('Asset Price ($)', fontsize=11)
ax.set_xlabel('Timeline (Ticks)', fontsize=11)
ax.grid(True, linestyle='--', alpha=0.2, color='#FFFFFF')

# PERFORMANCE ADVANTAGE: Initialize empty line plots ONCE outside the main loop.
# We modify these objects directly inside the frame loop instead of reinstantiating them.
line_price, = ax.plot([], [], color='#8E44AD', label='Stock Price (Tick)', lw=1.5, alpha=0.8)
line_fast, = ax.plot([], [], color='#3498DB', label='Fast EMA', lw=2.0)
line_slow, = ax.plot([], [], color='#E67E22', label='Slow EMA', lw=2.2)

# Dynamic text metrics block mapped into upper axis coordinates
metric_text = ax.text(0.02, 0.95, '', transform=ax.transAxes, fontsize=10,
                      fontfamily='monospace', bbox=dict(facecolor='#111111', alpha=0.6))

# Keep track of markers dynamically rendered on screen to handle cleanup properly
scatter_markers = []

# Add legend to canvas
ax.legend(loc='lower left', framealpha=0.5)


# ==============================================================================
# RENDERING ANIMATION ENGINE
# ==============================================================================
def init():
    """Establishes clear base states for all tracked object buffers."""
    line_price.set_data([], [])
    line_fast.set_data([], [])
    line_slow.set_data([], [])
    metric_text.set_text('')
    return line_price, line_fast, line_slow, metric_text


def animate(frame):
    """
    Executes core update steps per frame tick. Computes data changes,
    manages viewport window shifts, and updates canvas pointers efficiently.
    """
    global scatter_markers

    # 1. Inject fresh synthetic data to backend queue
    stream.generate_next_tick(frame)

    # 2. Window Sliding Viewport Adjustment
    # Shifts the viewport domain to give the visual illusion of a continuous scrolling chart
    if frame >= WINDOW_SIZE:
        ax.set_xlim(frame - WINDOW_SIZE, frame)
    else:
        ax.set_xlim(0, WINDOW_SIZE)

    # 3. Dynamic Y-Axis Scale Management
    # Auto-scales bounds based exclusively on values currently active in the view buffer
    current_min = min(stream.prices)
    current_max = max(stream.prices)
    padding = (current_max - current_min) * 0.15  # 15% clear space top/bottom
    ax.set_ylim(current_min - padding, current_max + padding)

    # 4. Update plot data handles directly (highly optimized performance path)
    line_price.set_data(stream.time_steps, stream.prices)
    line_fast.set_data(stream.time_steps, stream.fast_ema)
    line_slow.set_data(stream.time_steps, stream.slow_ema)

    # 5. Advanced Trigger: Real-time Crossover Catcher
    # Clean out markers from the previous render step to keep frame updates fast
    for marker in scatter_markers:
        marker.remove()
    scatter_markers.clear()

    # If we have enough history to detect crosses, analyze the final two periods
    if len(stream.prices) >= 2:
        f_prev, f_curr = stream.fast_ema[-2], stream.fast_ema[-1]
        s_prev, s_curr = stream.slow_ema[-2], stream.slow_ema[-1]

        # Golden Cross (Bullish Indicator: Fast line crosses ABOVE Slow line)
        if f_prev <= s_prev and f_curr > s_curr:
            g_mark = ax.scatter(frame, f_curr, color='#2ECC71', s=120, marker='^', zorder=5)
            scatter_markers.append(g_mark)
        # Death Cross (Bearish Indicator: Fast line crosses BELOW Slow line)
        elif f_prev >= s_prev and f_curr < s_curr:
            d_mark = ax.scatter(frame, f_curr, color='#E74C3C', s=120, marker='v', zorder=5)
            scatter_markers.append(d_mark)

    # 6. Keep data HUD metrics updated
    metric_text.set_text(
        f"Tick Frame: {frame}\n"
        f"Price:      ${stream.current_price:.2f}\n"
        f"Fast EMA:   ${stream.last_fast:.2f}\n"
        f"Slow EMA:   ${stream.last_slow:.2f}"
    )

    # Return updated elements to the animation subsystem
    return [line_price, line_fast, line_slow, metric_text] + scatter_markers


# ==============================================================================
# EXECUTION ENTRY POINT
# ==============================================================================
# blit=False is used because we are dynamically modifying axis limits (set_xlim/set_ylim)
# and cleaning up scatter collections continuously.
ani = animation.FuncAnimation(
    fig,
    animate,
    init_func=init,
    frames=2000,
    interval=UPDATE_INTERVAL,
    blit=False,
    repeat=False
)

plt.show()
