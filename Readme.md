# Astroboy

Astroboy is a Python-based pipeline for processing astronomical photometry data from `.raw` files. It extracts star counts, computes magnitudes, determines color indices, and estimates stellar temperatures.

## Features
- Loads and processes `.raw` astronomical data
- Extracts star and sky counts for B and V filters
- Computes B-band and V-band magnitudes
- Calculates color index (B - V) and estimates temperature
- GUI interface for user-friendly interaction
- Supports standalone executable generation using PyInstaller

## Installation

### Prerequisites
- Python 3.x
- Virtual environment (optional but recommended)

### Setting Up the Environment
```sh
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
.\.venv\Scripts\activate    # On Windows
pip install -r requirements.txt
```

## Running the Application

To run the GUI-based pipeline:
```sh
python star.py
```

## Creating a Standalone Executable
To generate a standalone executable, use PyInstaller:
```sh
pyinstaller --onefile --windowed --icon logo.ico --name Astroboy star.py
```
This will create an executable named `Astroboy` (or `Astroboy.exe` on Windows) in the `dist/` directory.

## Usage

### GUI Mode
1. Launch the application.
2. Select a `.raw` data file.
3. The application processes the file and displays computed magnitudes, color indices, and estimated temperatures.

### CLI Mode
Modify `star.py` to run without the GUI by manually invoking:
```python
pipeline = StarPipeline("path/to/file.raw")
star_data, B_mag, V_mag, B_V, temp = pipeline.run()
print(star_data, B_mag, V_mag, B_V, temp)
```

## File Format
The `.raw` file should contain astronomical observation data with the following format:
```
Date       Time       Object  Filter  Count1 Count2 Count3 Count4
DD-MM-YYYY HH:MM:SS  Name    [B/V]   int    int    int    int
```
Example:
```
12-03-2024 20:15:30  STAR1   B       1200   1220   1180   1210
12-03-2024 20:16:00  SKY     B       300    320    310    290
```

## Formulae Used

### Magnitude Calculation
The magnitude for each filter is calculated using the formula:
\[
M = -2.5 \times \log_{10}(S_{\text{star}} - S_{\text{sky}})
\]
where:
- \( S_{\text{star}} \) is the mean star count.
- \( S_{\text{sky}} \) is the mean sky count.

### Color Index (B - V)
The color index is computed as:
\[
(B - V) = M_B - M_V
\]
where:
- \( M_B \) is the magnitude in the B-band.
- \( M_V \) is the magnitude in the V-band.

### Temperature Estimation
The stellar temperature is estimated using:
\[
T = 10^{(3.988 - 0.881(B - V) + 0.769(B - V)^2 - 0.537(B - V)^3)}
\]
where \( B - V \) is the color index.

## License
This project is released under the MIT License.

## Author
Developed by [Yash Gadbail](https://github.com/yashgadbail)

