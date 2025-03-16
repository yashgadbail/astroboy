import numpy as np
import re
import os
import tkinter as tk
from tkinter import filedialog, messagebox

class StarPipeline:
    def __init__(self, filepath):
        self.filepath = filepath
        self.raw_data = None
        self.star_data = {}
        self.sky_b_counts = [] 
        self.sky_v_counts = [] 
        self.B_magnitude = None
        self.V_magnitude = None
        self.B_V = None
        self.temperature = None

    def load_data(self):
        """Loads the .raw file content."""
        try:
            with open(self.filepath, "r") as file:
                self.raw_data = file.readlines()
        except Exception as e:
            raise Exception(f"Error loading file: {e}")

    def preprocess(self):
        """Extracts relevant data and separates star and sky counts."""
        if not self.raw_data or len(self.raw_data) < 5:
            raise Exception("Invalid file format. Missing data.")

        data_lines = self.raw_data[4:]

        pattern = r"(\d{2}-\d{2}-\d{4})\s+(\d{2}:\d{2}:\d{2})\s+([A-Za-z\s]+)\s+([VB])\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)"

        for line in data_lines:
            match = re.search(pattern, line)
            if match:
                object_name = match.group(3).strip() 
                filter_band = match.group(4) 
                counts = list(map(int, match.groups()[5:])) 

                if object_name == "SKY":
                    if filter_band == "B":
                        self.sky_b_counts.append(np.mean(counts))
                    elif filter_band == "V":
                        self.sky_v_counts.append(np.mean(counts))
                else:
                    if object_name not in self.star_data:
                        self.star_data[object_name] = {'B': [], 'V': []}
                    
                    if filter_band == "B":
                        self.star_data[object_name]['B'].append(np.mean(counts))
                    elif filter_band == "V":
                        self.star_data[object_name]['V'].append(np.mean(counts))

    def calculate_magnitude(self, star_counts, sky_counts):
        """Computes magnitude from counts."""
        if not star_counts or not sky_counts:
            return float('nan') 

        S_star = np.mean(star_counts)
        S_sky = np.mean(sky_counts)

        if S_star <= S_sky:
            return float('nan') 

        return -2.5 * np.log10(S_star - S_sky)

    def compute_metrics(self):
        """Calculates magnitude, color index, and temperature."""
        self.B_magnitude = self.calculate_magnitude(self.sky_b_counts, self.sky_b_counts)
        self.V_magnitude = self.calculate_magnitude(self.sky_v_counts, self.sky_v_counts)

        if not np.isnan(self.B_magnitude) and not np.isnan(self.V_magnitude):
            self.B_V = self.B_magnitude - self.V_magnitude
        else:
            self.B_V = float('nan')

        if not np.isnan(self.B_V):
            self.temperature = 10 ** (3.988 - 0.881 * self.B_V + 0.769 * (self.B_V ** 2) - 0.537 * (self.B_V ** 3))
        else:
            self.temperature = float('nan')

    def run(self):
        """Executes the pipeline steps."""
        self.load_data()
        self.preprocess()
        self.compute_metrics()
        return self.star_data, self.B_magnitude, self.V_magnitude, self.B_V, self.temperature

def run_pipeline_gui():
    def open_file():
        file_path = filedialog.askopenfilename(filetypes=[("RAW Files", "*.raw")])
        if file_path:
            try:
                pipeline = StarPipeline(file_path)
                star_data, B_mag, V_mag, B_V, temp = pipeline.run()

                results_text.delete(1.0, tk.END)

                results_text.insert(tk.END, "\n---- Star Results ----\n")
                for star_name, counts in star_data.items():
                    B_star = counts['B']
                    V_star = counts['V']

                    B_magnitude = pipeline.calculate_magnitude(B_star, pipeline.sky_b_counts)
                    V_magnitude = pipeline.calculate_magnitude(V_star, pipeline.sky_v_counts)

                    B_V = B_magnitude - V_magnitude if not np.isnan(B_magnitude) and not np.isnan(V_magnitude) else float('nan')

                    if not np.isnan(B_V):
                        temperature = 10 ** (3.988 - 0.881 * B_V + 0.769 * (B_V ** 2) - 0.537 * (B_V ** 3))
                    else:
                        temperature = float('nan')

                    results_text.insert(tk.END, f"\nStar: {star_name}\n")
                    results_text.insert(tk.END, f"B-band Magnitude: {B_magnitude:.2f}\n" if not np.isnan(B_magnitude) else "Error: Invalid B-band magnitude\n")
                    results_text.insert(tk.END, f"V-band Magnitude: {V_magnitude:.2f}\n" if not np.isnan(V_magnitude) else "Error: Invalid V-band magnitude\n")
                    results_text.insert(tk.END, f"Color Index (B - V): {B_V:.2f}\n" if not np.isnan(B_V) else "Error: Invalid color index\n")
                    results_text.insert(tk.END, f"Estimated Temperature: {temperature:.2f} K\n" if not np.isnan(temperature) else "Error: Invalid temperature calculation\n")

            except Exception as e:
                messagebox.showerror("Pipeline Error", str(e))

    root = tk.Tk()
    root.title("Star Pipeline")
    root.geometry("600x400")

    open_button = tk.Button(root, text="Open RAW File", command=open_file)
    open_button.pack(pady=10)

    results_text = tk.Text(root, width=80, height=20)
    results_text.pack(pady=10)

    root.mainloop()

# Run the GUI
if __name__ == "__main__":
    run_pipeline_gui()
