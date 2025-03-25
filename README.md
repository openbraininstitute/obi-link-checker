# Link Checker with Selenium & Pytest

A Selenium &amp; Pytest-based automation framework for detecting broken links on a webpage. It validates hyperlink status codes and ensures all links are functional. Supports CI/CD integration for continuous monitoring.
The site under test is the Open Brain Platform. 


## Prerequisites

Ensure you have the following installed:

- Python (>= 3.8)
- Google Chrome (or another supported browser)
- ChromeDriver (matching your Chrome version)

## Installation

1. Clone this repository:

```
git clone git@github.com:ayimaok/webpage-link-checker.git
cd website-link-checker
```

2. Create a virtual environment (optional but recommended):

#### Install uv
Before setting up your virtual environment, make sure to install uv.
Follow these steps:

- For Linux and macOS:
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Using uv (recommended):**

```uv venv -p 3.11```

**Alternatively, using virtualenv:**

```
python -m venv venv
source .venv/bin/activate  
```

3. Install dependencies:
```
uv pip install -r requirements.txt
```
Usage

Run the link checker with:
```
uv run pytest tests/test_links.py --env=production -sv

```
### Test Artifacts, Logs, and Reports
* Broken links will be logged in broken_links.log file.
* Working links will be logged in working_links.log file.

## License

Copyright © 2025 Open Brain Institute
