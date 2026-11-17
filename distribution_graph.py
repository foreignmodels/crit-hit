import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from matplotlib.ticker import PercentFormatter

NORMAL, FLAT, FIGHTS = 80, 100, 1000
MAX_ATTACKS = 100

def main():
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(11, 7))
    fig.subplots_adjust(left=0.12, right=0.95, top=0.89, bottom=0.38)
    fig.suptitle('Critical Hit Damage Distribution', fontsize=20, y=0.97)
    results = fig.text(0.5, 0.265, '', ha='center', fontsize=11)
    fig.text(0.5, 0.035,
             '1,000 simulated fights',
             ha='center', fontsize=10)
    ax.set_xlabel('Total Damage')
    ax.set_ylabel('Percentage of simulated fights')
    ax.yaxis.set_major_formatter(PercentFormatter(100))
    ax.grid(axis='y', alpha=0.15)
    bars = ax.bar(np.arange(MAX_ATTACKS + 1), np.zeros(MAX_ATTACKS + 1),
                  color='#ffb454', label='Crit build')
    flat_line = ax.axvline(10 * FLAT, color='#42b9f5', linewidth=2,
               label='Flat build')
    ax.legend(loc='upper right')

    chance = Slider(fig.add_axes([0.28, 0.20, 0.48, 0.025]),
                    'Critical Hit Chance (%)', 0, 100, valinit=10, valstep=1, valfmt='%.0f%%')
    bonus = Slider(fig.add_axes([0.28, 0.145, 0.48, 0.025]),
                   'Critical Hit Multiplier (%)', 0, 200, valinit=100, valstep=5, valfmt='%.0f%%')
    attacks = Slider(fig.add_axes([0.28, 0.09, 0.48, 0.025]),
                    'Number of attacks', 1, MAX_ATTACKS, valinit=10, valstep=1, valfmt='%.0f')
    button = Button(fig.add_axes([0.83, 0.125, 0.12, 0.055]), 'Reset Sliders',
                    color='#23354a', hovercolor='#385575')
    cached_key, frequencies = None, None

    def update(_=None):
        nonlocal cached_key, frequencies
        c, b, n = chance.val / 100, bonus.val / 100, int(attacks.val)
        key = (c, n)
        # A bonus change only moves the bars; it doesn't need new random rolls.
        if key != cached_key:
            rolls = np.random.default_rng(42).binomial(n, c, size=FIGHTS)
            frequencies = np.bincount(rolls, minlength=n + 1) / FIGHTS
            cached_key = key
        totals = NORMAL * (n + np.arange(n + 1) * b)
        heights = frequencies * 100
        if b == 0:  # All crit counts now produce the same total damage.
            heights = np.zeros(n + 1)
            heights[0] = 100
        observed = totals[frequencies > 0]
        flat_total = n * FLAT
        low, high = min(observed[0], flat_total), max(observed[-1], flat_total)
        margin = max(NORMAL * b * 0.5, (high - low) * 0.08)
        width = max(1, NORMAL * b * 0.35)
        for i, bar in enumerate(bars):
            visible = i <= n and heights[i] > 0
            bar.set_visible(visible)
            if visible:
                bar.set_x(totals[i] - width / 2)
                bar.set_width(width)
                bar.set_height(heights[i])
        flat_line.set_xdata([flat_total, flat_total])
        ax.set_xlim(low - margin, high + margin)
        ax.set_ylim(0, min(110, max(10, heights.max() * 1.3)))
        expected_total = n * ((1 - c) * NORMAL + c * NORMAL * (1 + b))
        average = np.dot(frequencies, totals)
        variance = np.dot(frequencies, (totals - average) ** 2)
        results.set_text(
            f'Crit build  •  Expected total: {expected_total:,.2f}  |  '
            f'Simulated average: {average:,.2f}  |  Variance: {variance:,.2f}\n'
            f'Flat build  •  Average: {flat_total:,.2f}  |  Variance: 0.00')
        fig.canvas.draw_idle()

    def reset_sliders(_event):
        for slider in (chance, bonus, attacks):
            slider.reset()

    for slider in (chance, bonus, attacks):
        slider.on_changed(update)
    button.on_clicked(reset_sliders)
    # Keep the widgets alive while the interactive window is open.
    fig.controls = (chance, bonus, attacks, button)
    update()
    return fig


if __name__ == '__main__':
    main()
    plt.show()