# Deep Lynx Query Package

A minimal package for querying Deep Lynx Product and Lot data and calculating statistics.

## Structure
```
deep_lynx_package/
├── README.md              # This file
├── requirements.txt       # Dependencies
├── .env.example          # Example environment variables
├── src/
│   ├── __init__.py
│   ├── config.py         # Configuration handling
│   ├── query.py          # Deep Lynx query functionality
│   ├── process.py        # Data processing and statistics
│   └── run.py           # Main workflow script
```

## Setup
1. Copy `.env.example` to `.env` and fill in your Deep Lynx credentials
2. Install dependencies: `pip install -r requirements.txt`
3. Run the workflow: `python src/run.py`

## Environment Variables
```
DEEP_LYNX_URL=http://localhost:8090
DEEP_LYNX_CONTAINER_ID=5
DEEP_LYNX_API_KEY=your_api_key
DEEP_LYNX_API_SECRET=your_api_secret
```

## Usage
```python
from src.run import run_workflow
result = run_workflow()
print(result)
``` 