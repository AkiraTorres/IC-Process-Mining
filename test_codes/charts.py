import matplotlib.pyplot as plt
import pandas as pd

# Load the CSV file
file_path = "../sceneries_results/general_info.csv"  # Update with the correct path
data = pd.read_csv(file_path, delimiter=";")

# Columns for the first line chart
columns_line_chart_1 = ["longest_sequence_length", "average_sequence_length"]

# Columns for the second line chart
columns_line_chart_2 = ["longest_pattern_length", "average_pattern_length"]


def plot_sequence_length():
    # Create the first line chart with overlapping lines
    # Assuming data and columns_line_chart_1 are defined
    plt.figure(figsize=(14, 8))
    # Plot each column in columns_line_chart_1
    for column in columns_line_chart_1:
        plt.plot(data["sceneries"], data[column], marker="o", linestyle="-", label=column)
        # Annotate each data point with its y-value
        for x, y in zip(data["sceneries"], data[column]):
            plt.text(x, y, f"{y}", ha="center", va="bottom", fontsize=10)  # Adjust fontsize as needed
    plt.xlabel("Sceneries")
    plt.ylabel("Values")
    plt.title("Line Charts of Longest and Average Sequence Length")
    plt.legend()
    plt.xticks(rotation=45)
    # Adjust y-axis limits to ensure all y-values are visible
    plt.ylim(bottom=0)  # Set the lower limit of y-axis to 0 or adjust as needed
    plt.grid(True)
    plt.tight_layout()  # Adjust layout to make sure all elements fit properly
    # Save the first line chart as PNG
    plt.savefig("sceneries_results/line_chart_sequence_length.png")
    plt.show()


def plot_pattern_length():
    # Create the second line chart with overlapping lines
    # Assuming data and columns_line_chart_2 are defined
    plt.figure(figsize=(14, 8))
    # Plot each column in columns_line_chart_2
    for column in columns_line_chart_2:
        plt.plot(data["sceneries"], data[column], marker="o", linestyle="-", label=column)
        # Annotate each data point with its y-value
        for x, y in zip(data["sceneries"], data[column]):
            plt.text(x, y, f"{y}", ha="center", va="bottom", fontsize=10)  # Adjust fontsize as needed
    plt.xlabel("Sceneries")
    plt.ylabel("Values")
    plt.title("Line Charts of Longest and Average Pattern Length")
    plt.legend()
    plt.xticks(rotation=45)
    # Adjust y-axis limits to ensure all y-values are visible
    plt.ylim(bottom=0)  # Set the lower limit of y-axis to 0 or adjust as needed
    plt.grid(True)
    plt.tight_layout()  # Adjust layout to make sure all elements fit properly
    # Save the second line chart as PNG
    plt.savefig("sceneries_results/line_chart_pattern_length.png")
    plt.show()


def plot_total_sequences():
    # Create a horizontal bar chart for 'total_sequences'
    plt.figure(figsize=(14, 8))
    bars = plt.barh(data["sceneries"], data["total_sequences"], color="skyblue")
    plt.xlabel("Total Sequences")
    plt.ylabel("Sceneries")
    plt.title("Horizontal Bar Chart of Total Sequences")
    # Customize grid appearance
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)
    plt.gca().set_axisbelow(True)  # Ensure grid is behind the bars
    plt.tight_layout()
    # Add values on the bars
    for bar in bars:
        plt.text(
            bar.get_width(),
            bar.get_y() + bar.get_height() / 2,
            f"{bar.get_width()}",
            va="center",
            ha="left",
            fontsize=8,
        )
    # Save the horizontal bar chart for total sequences as PNG
    plt.savefig("sceneries_results/bar_chart_total_sequences.png")
    plt.show()


def plot_elapsed_time():
    # Create a horizontal bar chart for 'elapsed_time'
    plt.figure(figsize=(14, 8))
    bars = plt.barh(data["sceneries"], data["elapsed_time"], color="lightcoral")
    plt.xlabel("Elapsed Time (seconds)")
    plt.ylabel("Sceneries")
    plt.title("Horizontal Bar Chart of Elapsed Time")
    # Customize grid appearance
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)
    plt.gca().set_axisbelow(True)  # Ensure grid is behind the bars
    plt.tight_layout()
    # Add values on the bars
    for bar in bars:
        plt.text(
            bar.get_width(),
            bar.get_y() + bar.get_height() / 2,
            f"{bar.get_width()}",
            va="center",
            ha="left",
            fontsize=8,
        )
    # Save the horizontal bar chart for elapsed time as PNG
    plt.savefig("sceneries_results/bar_chart_elapsed_time.png")
    plt.show()


if __name__ == "__main__":
    plot_sequence_length()
    plot_pattern_length()
    plot_total_sequences()
    plot_elapsed_time()
