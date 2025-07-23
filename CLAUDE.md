# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Running the Application
```bash
python app.py
```
The Flask development server runs on `http://localhost:5000` with debug mode enabled.

### Environment Setup
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Dependencies
Install from requirements.txt which includes: Flask, Dash, Pandas, Plotly, and NumPy.

## Architecture

This is a Flask-based trading dashboard that visualizes trading performance data from a `trades.json` file.

### Core Components

**app.py** - Main Flask application with the following key functions:
- `load_trades()` - Loads trading data from trades.json
- `calculate_metrics()` - Computes basic P&L metrics, win rates, and averages
- `calculate_daily_cumulative_pnl()` - Builds time series data for cumulative P&L chart
- `compute_dashboard_stats()` - Calculates detailed statistics (day of week analysis, trade durations, best/worst trades)
- `compute_calendar_data()` - Generates calendar view data with daily/weekly/monthly stats

**Data Structure** - The application expects trades.json with this format:
```json
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
```

**Frontend** - Single-page application using:
- Tailwind CSS for styling with dark theme
- Plotly.js for interactive charts
- JavaScript for calendar interactions and trade detail popups
- Account filtering and month/year navigation

### Routes
- `/` - Main dashboard with metrics, charts, and calendar
- `/trades/<date>` - API endpoint returning trades for a specific date

### Key Features
- Account-based filtering
- Monthly calendar view with daily P&L
- Cumulative P&L time series chart
- Comprehensive trading statistics
- Interactive trade details on calendar click