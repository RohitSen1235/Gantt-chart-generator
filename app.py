import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import timedelta
import numpy as np

# Define the task information
tasks = [
    {"Task": "Structure Design", "Responsibility": "Lalanthika", "Start date": "1-Nov-2024", "End Date": "15-Dec-2024"},
    {"Task": "Design Drawings ", "Responsibility": "Lalanthika", "Start date": "15-Dec-2024", "End Date": "30-Dec-2024"},
    {"Task": "Manufacturing of Print head module", "Responsibility": "Rohit", "Start date": "1-Jan-2025", "End Date": "30-Jan-2025"},
    {"Task": "Finalysing the BOM", "Responsibility": "Shilpesh", "Start date": "1-Dec-2024", "End Date": "15-Dec-2024"},
    {"Task": "Finalising PLC components", "Responsibility": "Jalath", "Start date": "1-Dec-2024", "End Date": "15-Dec-2024"},
    {"Task": "Finalysing X,Y actuators", "Responsibility": "Lalanthika", "Start date": "1-Dec-2024", "End Date": "20-Dec-2024"},
    {"Task": "Finalysing Sand Mixer", "Responsibility": "Shilpesh", "Start date": "1-Dec-2024", "End Date": "20-Dec-2024"},
    {"Task": "Lead time Printhead", "Responsibility": "Rohit", "Start date": "1-Jan-2025", "End Date": "15-Feb-2025"},
    {"Task": "Lead time Electronics", "Responsibility": "Rohit", "Start date": "1-Jan-2025", "End Date": "15-Feb-2025"},
    {"Task": "Lead Time Ink Delivery system", "Responsibility": "Rohit", "Start date": "1-Jan-2025", "End Date": "20-Feb-2025"},
    {"Task": "Assembly", "Responsibility": "Jalath", "Start date": "20-Feb-2025", "End Date": "5-Mar-2025"},
    {"Task": "Pilot Print Job", "Responsibility": "Jalath", "Start date": "10-Mar-2025", "End Date": "12-Mar-2025"},
]

# Sort the tasks by start date
sorted_tasks = sorted(tasks, key=lambda x: mdates.datestr2num(x["Start date"]),reverse=True)

# Assign different colors to responsibilities
responsibilities = set(task["Responsibility"] for task in sorted_tasks)
colors = plt.colormaps["tab20c"](np.linspace(0, 1, len(responsibilities)))

# Create a figure and axis
fig, ax = plt.subplots(figsize=(12, 8))

# Convert the date strings to datetime objects
start_dates = [mdates.datestr2num(task["Start date"]) for task in sorted_tasks]
end_dates = [mdates.datestr2num(task["End Date"]) for task in sorted_tasks]

# Set the y-axis limits
ax.set_ylim(0, len(sorted_tasks))

# Set the y-ticks and labels
yticks = range(len(sorted_tasks))
ytick_labels = [task["Task"] for task in sorted_tasks]
ax.set_yticks(yticks)
ax.set_yticklabels(ytick_labels)

# Plot the tasks
for i, task in enumerate(sorted_tasks):
    start_date = mdates.datestr2num(task["Start date"])
    end_date = mdates.datestr2num(task["End Date"])
    duration = end_date - start_date

    responsibility = task["Responsibility"]
    color = colors[list(responsibilities).index(responsibility)]

    ax.broken_barh([(start_date, duration)], (i, 0.6), facecolors=color, edgecolor='black')

# Set the x-axis limits and ticks
min_date = min(start_dates)
max_date = max(end_dates)
ax.set_xlim(min_date, max_date)
ax.xaxis.set_major_locator(mdates.WeekdayLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))

# Convert float values to datetime objects
min_date = mdates.num2date(min_date)
max_date = mdates.num2date(max_date)

# Add vertical lines for each day
for date in mdates.drange(min_date, max_date + timedelta(days=1), timedelta(days=1)):
    ax.axvline(date, color='gray', linestyle='--', linewidth=0.5)

# Set the chart title and labels
plt.title("Project Timeline Sand Printer")
plt.xlabel("Timeline")
plt.ylabel("Task")

# Create a legend for responsibilities
handles = [plt.Rectangle((0, 0), 1, 1, color=colors[i]) for i, r in enumerate(responsibilities)]
labels = list(responsibilities)
plt.legend(handles, labels, loc="upper right")

# Adjust the layout and padding
plt.tight_layout()

# Save the plot instead of showing it
plt.savefig('gantt_chart.png')
plt.close()
