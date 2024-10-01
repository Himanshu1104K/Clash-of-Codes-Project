import matplotlib
matplotlib.use('Agg')  # Use Agg backend for rendering to file
from flask import Flask, send_file
import matplotlib.pyplot as plt
import pandas as pd
from itertools import count
import io

index = count()  # Generator to simulate real-time data updates
df = pd.read_csv("data.csv")  # Load your CSV data

app = Flask(__name__)

# Function to generate and update the plot
def animate():
    current_index = next(index)  # Get the next index
    if current_index >= len(df):
        current_index = len(df) - 1  # Prevent going out of bounds

    # Create the figure and clear previous plots
    fig, ax = plt.subplots()
    ax.plot(df.index[:current_index+1], df["efficiency"][:current_index+1], label="Efficiency")
    ax.set_xlabel("Current Data Index")
    ax.set_ylabel("Efficiency")
    ax.set_title("Real-Time Efficiency Data")
    ax.legend()
    plt.tight_layout()

    # Save the plot to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png')
    plt.close(fig)  # Close the figure to avoid memory leaks
    img.seek(0)
    return img

# Flask route to serve the plot
@app.route("/plot")
def plot_graph():
    img = animate()  # Call the animate function to generate the plot
    return send_file(img, mimetype="image/png")

if __name__ == "__main__":
    app.run(debug=True)
