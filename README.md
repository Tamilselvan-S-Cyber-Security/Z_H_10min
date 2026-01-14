# Z_H_10min - Web Application Testing Tool

A powerful command-line tool for web application testing using Selenium WebDriver. This tool helps in performing basic web application security and functionality tests.

## Features

- URL reachability testing
- Page loading verification
- Console error checking
- Broken link detection
- Screenshot capture
- Headless mode support
- Colorized console output
- Easy to use CLI interface

## Installation

1. Make sure you have Python 3.7+ installed
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python web_tester.py https://example.com
```

### Headless Mode

```bash
python web_tester.py https://example.com --headless
```

### Interactive Mode

If you don't provide a URL as an argument, the tool will prompt you to enter one:

```bash
python web_tester.py
```

## Output

The tool provides color-coded output:
- Green: Successful operations
- Yellow: Warnings
- Red: Errors
- Cyan: Information

## Screenshots

Screenshots are automatically saved in the current directory with timestamps in the filename (e.g., `screenshot_20250101_123456.png`).

## Developer

- **Name:** Tamilselvan S
- **Role:** Security Researcher

## License

This tool is for educational and security research purposes only. Use responsibly and only on systems you have permission to test.
