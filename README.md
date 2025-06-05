# Trading Dashboard

A Flask-based web application for visualizing and analyzing trading performance. The dashboard provides comprehensive insights into trading metrics, P&L analysis, and daily trade details.

## Features

- Account-based filtering
- Performance metrics (Total P&L, Win Rate, Average Win/Loss)
- Daily cumulative P&L chart
- Interactive calendar view with trade details
- Detailed statistics including:
  - Most active/profitable days
  - Trade durations
  - Best/worst trades
  - Trade direction analysis

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/trading-dashboard.git
cd trading-dashboard
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Place your trades data in `trades.json` with the following format:
```json
[
  {
    "id": "unique_id",
    "account_id": "account_number",
    "symbol": "ticker",
    "side": "LONG/SHORT",
    "quantity": number,
    "price": number,
    "close_price": number,
    "profit": number,
    "entry_time": "YYYY-MM-DD HH:MM:SS",
    "exit_time": "YYYY-MM-DD HH:MM:SS"
  }
]
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and navigate to `http://localhost:5000`

## Technologies Used

- Flask
- Plotly.js
- Tailwind CSS
- JavaScript

## License

MIT License 