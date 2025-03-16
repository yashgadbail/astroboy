import numpy as np
import re
import os

def parse_file(file_path):
    """
    Parse .raw file and extract stellar counts.
    
    Args:
        file_path (str): Path to the .raw file
        
    Returns:
        tuple: (star_data dict, sky_b_counts list, sky_v_counts list)
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    star_data = {}
    sky_b_counts = []
    sky_v_counts = []

    try:
        with open(file_path, "r") as file:
            lines = file.readlines()
    except IOError as e:
        raise IOError(f"Error reading file: {e}")

    data_lines = lines[4:]

    pattern = r"(\d{2}-\d{2}-\d{4})\s+(\d{2}:\d{2}:\d{2})\s+([C])?\s*(\w+)\s+([VB])\s+(\d{5})\s+(\d{5})\s+(\d{5})\s+(\d{5})"

    for line in data_lines:
        match = re.search(pattern, line)
        if match:
            object_name = match.group(4).strip()
            filter_band = match.group(5)
            counts = [int(x) for x in match.groups()[5:9]]
            mean_counts = np.mean(counts)

            if object_name == "SKY":
                if filter_band == "B":
                    sky_b_counts.append(mean_counts)
                elif filter_band == "V":
                    sky_v_counts.append(mean_counts)
            else:
                if object_name not in star_data:
                    star_data[object_name] = {'B': [], 'V': []}
                
                if filter_band == "B":
                    star_data[object_name]['B'].append(mean_counts)
                elif filter_band == "V":
                    star_data[object_name]['V'].append(mean_counts)
    
    return star_data, sky_b_counts, sky_v_counts

def calculate_magnitude(star_counts, sky_counts):
    """
    Calculate magnitude from star and sky counts.
    
    Args:
        star_counts (list): List of star counts
        sky_counts (list): List of sky counts
        
    Returns:
        float: Calculated magnitude or nan if invalid
    """
    if not star_counts or not sky_counts:
        return float('nan')
    
    star_mean = np.mean(star_counts)
    star_std = np.std(star_counts)
    filtered_star_counts = [x for x in star_counts if abs(x - star_mean) < 2 * star_std]
    
    S_star = np.mean(filtered_star_counts) if filtered_star_counts else np.mean(star_counts)
    S_sky = np.mean(sky_counts)
    
    if S_star <= S_sky:
        return float('nan')
    
    return -2.5 * np.log10(S_star - S_sky)


def estimate_temperature(B_V):
    """
    Estimate star temperature from B-V color index.
    
    Args:
        B_V (float): B-V color index
        
    Returns:
        float: Estimated temperature in Kelvin or nan if invalid
    """
    if np.isnan(B_V):
        return float('nan')
    return 10**(3.988 - 0.881 * B_V + 0.769 * (B_V ** 2) - 0.537 * (B_V ** 3))

if __name__ == "__main__":
    file_path = "D:/newnewnew/astroboy/content/Procyon.raw"

    try:
        star_data, sky_b_counts, sky_v_counts = parse_file(file_path)
        
        for star_name, counts in star_data.items():
            B_magnitude = calculate_magnitude(counts['B'], sky_b_counts)
            V_magnitude = calculate_magnitude(counts['V'], sky_v_counts)
            B_V = B_magnitude - V_magnitude if not np.isnan(B_magnitude) and not np.isnan(V_magnitude) else float('nan')
            temperature = estimate_temperature(B_V)
            
            print(f"\nResults for {star_name}:")
            print("-" * 40)
            print(f"Number of B measurements: {len(counts['B'])}")
            print(f"Number of V measurements: {len(counts['V'])}")
            print(f"B-band Magnitude: {B_magnitude:.3f}" if not np.isnan(B_magnitude) else "Error: Invalid B-band magnitude")
            print(f"V-band Magnitude: {V_magnitude:.3f}" if not np.isnan(V_magnitude) else "Error: Invalid V-band magnitude")
            print(f"Color Index (B-V): {B_V:.3f}" if not np.isnan(B_V) else "Error: Invalid color index")
            print(f"Estimated Temperature: {temperature:.0f} K" if not np.isnan(temperature) else "Error: Invalid temperature calculation")
            
    except Exception as e:
        print(f"Error: {str(e)}")