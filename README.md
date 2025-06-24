# Check Missing Images (cmi.py)

A cross-platform PyQt5 desktop application for verifying missing images for ROM files. The tool compares the files in a ROMs folder against image files in another folder (including subfolders), optionally using a filename prefix, and generates a log of missing images.

## Features

- **Graphical User Interface:** Easy-to-use PyQt5 interface.
- **ROM and Image Directory Selection:** Select folders for ROM files and their associated images.
- **Prefix Support:** Specify an optional prefix for image filenames.
- **Progress Bar:** Visual progress feedback during checking.
- **Detailed Log Output:** View and save logs of missing images and process details.
- **Cross-Platform:** Works on Windows and Linux.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/gegecom83/cmi.py.git
   cd cmi.py
   ```

2. **Install dependencies:**
   - Python 3.7+
   - PyQt5

   Install with pip:
   ```bash
   pip install PyQt5
   ```

## Usage

Run the application with Python:

```bash
python cmi.py
```

### Steps:

1. **Select ROMs Path:**  
   Click "Browse ROMs" and select the directory containing your ROM files (top-level files and `.cue` files in subfolders will be included).

2. **Select Images Path:**  
   Click "Browse Images" and select the directory containing your image files (all subfolders will be searched).

3. **(Optional) Set Prefix:**  
   Enter a prefix if your image files use one (e.g., `Sega_` to match `Sega_ROM1.png`).

4. **Check for Missing Images:**  
   Click "Check Missing Images" to start the scan. Progress and log output will be displayed.

5. **Save Log:**  
   Once the check is complete, click "Save Log" to export the results.

## Screenshot

![main](https://github.com/gegecom83/cmi.py/blob/main/main.png)

## Troubleshooting

- **PyQt5 not installed?**  
  Install with `pip install PyQt5`.

- **Permission errors or invalid paths?**  
  Ensure you have access to the selected folders and that they exist.

## License

MIT License

## Author

[gegecom83](https://github.com/gegecom83)
