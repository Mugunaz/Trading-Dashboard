from flask import Flask, render_template, jsonify, request, redirect, url_for
import json
from datetime import datetime, timedelta
import calendar
from collections import Counter, defaultdict

app = Flask(__name__)

def load_trades():
    with open('trades.json', 'r') as f:
        return json.load(f)

def calculate_metrics(trades):
    total_pl = sum(trade['profit'] for trade in trades)
    winning_trades = sum(1 for trade in trades if trade['profit'] > 0)
    total_trades = len(trades)
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    # Calculate average win and loss
    winning_profits = [trade['profit'] for trade in trades if trade['profit'] > 0]
    losing_profits = [trade['profit'] for trade in trades if trade['profit'] < 0]
    
    avg_win = sum(winning_profits) / len(winning_profits) if winning_profits else 0
    avg_loss = sum(losing_profits) / len(losing_profits) if losing_profits else 0
    
    return {
        'total_pl': total_pl,
        'win_rate': round(win_rate, 2),
        'winning_trades': winning_trades,
        'total_trades': total_trades,
        'avg_win': round(avg_win, 2),
        'avg_loss': round(avg_loss, 2)
    }

def calculate_daily_cumulative_pnl(trades):
    # Sort trades by exit_time
    trades_sorted = sorted(trades, key=lambda t: t['exit_time'])
    # Get all unique dates
    dates = sorted(list(set([t['exit_time'][:10] for t in trades_sorted])))
    if not dates:
        return [], []
    # Fill in missing days
    start_date = datetime.strptime(dates[0], "%Y-%m-%d")
    end_date = datetime.strptime(dates[-1], "%Y-%m-%d")
    all_dates = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range((end_date - start_date).days + 1)]
    # Calculate daily cumulative pnl
    cumulative = 0
    pnls = []
    trade_idx = 0
    for d in all_dates:
        # Add profits for trades closed on this day
        while trade_idx < len(trades_sorted) and trades_sorted[trade_idx]['exit_time'][:10] == d:
            cumulative += trades_sorted[trade_idx]['profit']
            trade_idx += 1
        pnls.append(cumulative)
    # Prepend zero at one day before the first date
    zero_date = (start_date - timedelta(days=1)).strftime("%Y-%m-%d")
    all_dates = [zero_date] + all_dates
    pnls = [0] + pnls
    return all_dates, pnls

def compute_dashboard_stats(trades):
    # Helper: parse datetime
    def parse_dt(s):
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")

    # Group by day of week
    day_counts = Counter()
    day_profits = defaultdict(float)
    day_trade_ids = defaultdict(list)
    for t in trades:
        day = calendar.day_name[parse_dt(t['entry_time']).weekday()]
        day_counts[day] += 1
        day_profits[day] += t['profit']
        day_trade_ids[day].append(t['id'])

    # Most active day
    most_active_day = day_counts.most_common(1)[0][0] if day_counts else None
    most_active_trades = day_counts[most_active_day] if most_active_day else 0
    most_active_days = len([d for d in day_counts if day_counts[d] == most_active_trades])
    most_active_avg = most_active_trades / most_active_days if most_active_days else 0

    # Most/least profitable day
    most_prof_day = max(day_profits, key=day_profits.get) if day_profits else None
    least_prof_day = min(day_profits, key=day_profits.get) if day_profits else None
    most_prof_val = day_profits[most_prof_day] if most_prof_day else 0
    least_prof_val = day_profits[least_prof_day] if least_prof_day else 0

    # Total trades/lots
    total_trades = len(trades)
    total_lots = sum(t['quantity'] for t in trades)

    # Durations
    durations = [(parse_dt(t['exit_time']) - parse_dt(t['entry_time'])).total_seconds() for t in trades]
    avg_trade_dur = sum(durations) / len(durations) if durations else 0
    win_durations = [d for d, t in zip(durations, trades) if t['profit'] > 0]
    loss_durations = [d for d, t in zip(durations, trades) if t['profit'] < 0]
    avg_win_dur = sum(win_durations) / len(win_durations) if win_durations else 0
    avg_loss_dur = sum(loss_durations) / len(loss_durations) if loss_durations else 0

    # Average win/loss
    winning_trades = [t for t in trades if t['profit'] > 0]
    losing_trades = [t for t in trades if t['profit'] < 0]
    avg_win = sum(t['profit'] for t in winning_trades) / len(winning_trades) if winning_trades else 0
    avg_loss = sum(t['profit'] for t in losing_trades) / len(losing_trades) if losing_trades else 0

    # Trade direction % (longs)
    long_trades = [t for t in trades if t['side'].upper() == 'LONG']
    trade_dir_pct = (len(long_trades) / total_trades * 100) if total_trades else 0

    # Best/worst trade
    best_trade = max(trades, key=lambda t: t['profit'], default=None)
    worst_trade = min(trades, key=lambda t: t['profit'], default=None)

    # Format durations
    def fmt_dur(seconds):
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        if h:
            return f"{h} hr {m:02d} min {s:02d} sec"
        else:
            return f"{m} min {s:02d} sec"

    return {
        'most_active_day': most_active_day,
        'most_active_days': most_active_days,
        'most_active_trades': most_active_trades,
        'most_active_avg': round(most_active_avg, 2),
        'most_prof_day': most_prof_day,
        'most_prof_val': most_prof_val,
        'least_prof_day': least_prof_day,
        'least_prof_val': least_prof_val,
        'total_trades': total_trades,
        'total_lots': total_lots,
        'avg_trade_dur': fmt_dur(avg_trade_dur),
        'avg_win_dur': fmt_dur(avg_win_dur),
        'avg_loss_dur': fmt_dur(avg_loss_dur),
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'trade_dir_pct': round(trade_dir_pct, 2),
        'best_trade': best_trade,
        'worst_trade': worst_trade
    }

def compute_calendar_data(trades, year=None, month=None):
    # Default to current month
    today = datetime.today()
    year = year or today.year
    month = month or today.month
    # Set calendar to start weeks on Sunday
    calendar.setfirstweekday(calendar.SUNDAY)
    # Get all trades for the month
    trades_in_month = [t for t in trades if datetime.strptime(t['exit_time'], "%Y-%m-%d %H:%M:%S").year == year and datetime.strptime(t['exit_time'], "%Y-%m-%d %H:%M:%S").month == month]
    # Build daily stats
    days_in_month = calendar.monthrange(year, month)[1]
    daily = {}
    for day in range(1, days_in_month + 1):
        date_str = f"{year}-{month:02d}-{day:02d}"
        day_trades = [t for t in trades_in_month if t['exit_time'].startswith(date_str)]
        daily[day] = {
            'pnl': sum(t['profit'] for t in day_trades),
            'count': len(day_trades)
        }
    # Build weekly stats
    weeks = calendar.monthcalendar(year, month)
    weekly = []
    for week in weeks:
        week_days = [d for d in week if d != 0]
        week_trades = [t for t in trades_in_month if int(t['exit_time'][8:10]) in week_days]
        weekly.append({
            'pnl': sum(t['profit'] for t in week_trades),
            'count': len(week_trades)
        })
    # Monthly stats
    month_pnl = sum(t['profit'] for t in trades_in_month)
    month_count = len(trades_in_month)
    month_name = calendar.month_name[month]
    return {
        'year': year,
        'month': month,
        'month_name': month_name,
        'days_in_month': days_in_month,
        'weeks': weeks,
        'daily': daily,
        'weekly': weekly,
        'month_pnl': month_pnl,
        'month_count': month_count
    }

@app.route('/')
def dashboard():
    trades = load_trades()
    # Get all unique account_ids as strings
    accounts = sorted(set(str(t.get('account_id')) for t in trades if 'account_id' in t))
    # Get selected account from query params
    selected_account = request.args.get('account_id')
    if selected_account:
        trades = [t for t in trades if str(t.get('account_id')) == selected_account]
    metrics = calculate_metrics(trades)
    pnl_dates, pnl_values = calculate_daily_cumulative_pnl(trades)
    stats = compute_dashboard_stats(trades)
    # Get year/month from query params
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    today = datetime.today()
    if year is None or month is None:
        return redirect(url_for('dashboard', year=today.year, month=today.month, account_id=selected_account if selected_account else None))
    calendar_data = compute_calendar_data(trades, year=year, month=month)
    return render_template(
        'index.html',
        metrics=metrics,
        daily_pnl_dates=pnl_dates,
        daily_pnl_values=pnl_values,
        stats=stats,
        calendar_data=calendar_data,
        current_year=today.year,
        current_month=today.month,
        accounts=accounts,
        selected_account=selected_account
    )

@app.route('/trades/<date>')
def get_trades_for_date(date):
    trades = load_trades()
    # Get selected account from query params
    selected_account = request.args.get('account_id')
    if selected_account:
        trades = [t for t in trades if str(t.get('account_id')) == selected_account]
    # Filter trades for the specific date
    day_trades = [t for t in trades if t['exit_time'].startswith(date)]
    return jsonify(day_trades)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
