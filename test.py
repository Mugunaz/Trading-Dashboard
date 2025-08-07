import pandas as pd
import json
from datetime import datetime
from pprint import pprint

def csv_to_dashboard_format(csv_file_path, account_id="CSV_ACCOUNT"):
    """
    Convert a trading journal CSV to Trading Dashboard format.
    
    Args:
        csv_file_path: Path to the CSV file
        account_id: Account ID to use for all trades (default: "CSV_ACCOUNT")
    
    Returns:
        list: List of dictionaries in Trading Dashboard format
    """
    
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file_path)
        
        print(f"Loaded {len(df)} trades from CSV")
        print(f"Columns: {list(df.columns)}")
        
        # Clean column names (remove extra spaces)
        df.columns = df.columns.str.strip()
        
        dashboard_trades = []
        
        for index, row in df.iterrows():
            try:
                # Extract data from CSV row
                ticket = str(row['Ticket'])
                open_time = row['Open']
                trade_type = row['Type'].lower().strip()
                volume = float(row['Volume'])
                symbol = row['Symbol']
                entry_price = float(row['Price'])
                close_time = row['Close']
                
                # Handle different close price column names (Price_1 or Price.1)
                if 'Price_1' in row and pd.notna(row['Price_1']):
                    exit_price = float(row['Price_1'])
                elif 'Price.1' in row and pd.notna(row['Price.1']):
                    exit_price = float(row['Price.1'])
                else:
                    # Try to find any column that might be the close price
                    close_price_cols = [col for col in df.columns if 'price' in col.lower() and col != 'Price']
                    if close_price_cols:
                        exit_price = float(row[close_price_cols[0]])
                    else:
                        print(f"Warning: No close price found for row {index}, using entry price")
                        exit_price = entry_price
                
                swap = float(row['Swap']) if pd.notna(row['Swap']) else 0
                commission = float(row['Commissions']) if pd.notna(row['Commissions']) else 0
                profit = float(row['Profit'])
                
                # Calculate total profit including swap and commissions
                total_profit = profit + swap + commission
                
                # Determine side (LONG/SHORT)
                side = "LONG" if trade_type == "buy" else "SHORT"
                
                # Format timestamps
                entry_time = pd.to_datetime(open_time).strftime('%Y-%m-%d %H:%M:%S')
                exit_time = pd.to_datetime(close_time).strftime('%Y-%m-%d %H:%M:%S')
                
                # Create trade dictionary in Dashboard format
                trade_dict = {
                    "id": f"csv_{ticket}_{index}",
                    "account_id": str(account_id),
                    "symbol": symbol,
                    "side": side,
                    "quantity": volume,
                    "price": entry_price,
                    "close_price": exit_price,
                    "profit": round(total_profit, 2),
                    "entry_time": entry_time,
                    "exit_time": exit_time
                }
                
                dashboard_trades.append(trade_dict)
                
            except Exception as e:
                print(f"Error processing row {index}: {e}")
                print(f"Row data: {row.to_dict()}")
                continue
        
        print(f"Successfully converted {len(dashboard_trades)} trades")
        return dashboard_trades
        
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []

def save_trades_to_json(trades, filename="trades.json"):
    """
    Save trades to JSON file in Trading Dashboard format.
    
    Args:
        trades: List of trade dictionaries
        filename: Output filename (default: trades.json)
    """
    try:
        with open(filename, 'w') as f:
            json.dump(trades, f, indent=2)
        print(f"✅ Trades saved to {filename}")
    except Exception as e:
        print(f"❌ Error saving trades to JSON: {e}")

def print_trades_summary(trades):
    """
    Print a summary of the trades data.
    
    Args:
        trades: List of trade dictionaries
    """
    if not trades:
        print("No trades to summarize")
        return
    
    total_trades = len(trades)
    total_profit = sum(trade['profit'] for trade in trades)
    winning_trades = sum(1 for trade in trades if trade['profit'] > 0)
    losing_trades = sum(1 for trade in trades if trade['profit'] < 0)
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    # Calculate additional metrics
    profits = [trade['profit'] for trade in trades if trade['profit'] > 0]
    losses = [trade['profit'] for trade in trades if trade['profit'] < 0]
    
    avg_win = sum(profits) / len(profits) if profits else 0
    avg_loss = sum(losses) / len(losses) if losses else 0
    
    symbols = list(set(trade['symbol'] for trade in trades))
    accounts = list(set(trade['account_id'] for trade in trades))
    
    print(f"\n{'='*60}")
    print("TRADING DASHBOARD FORMAT SUMMARY")
    print(f"{'='*60}")
    print(f"Total Trades: {total_trades}")
    print(f"Winning Trades: {winning_trades}")
    print(f"Losing Trades: {losing_trades}")
    print(f"Win Rate: {win_rate:.2f}%")
    print(f"Total Profit: ${total_profit:.2f}")
    print(f"Average Profit per Trade: ${total_profit/total_trades:.2f}")
    print(f"Average Win: ${avg_win:.2f}")
    print(f"Average Loss: ${avg_loss:.2f}")
    print(f"Profit Factor: {abs(avg_win/avg_loss):.2f}" if avg_loss != 0 else "N/A")
    print(f"Symbols Traded: {', '.join(symbols)}")
    print(f"Accounts: {', '.join(accounts)}")
    
    if trades:
        # Sort trades by entry time to get date range
        sorted_trades = sorted(trades, key=lambda x: x['entry_time'])
        print(f"\nDate Range:")
        print(f"First Trade: {sorted_trades[0]['entry_time']}")
        print(f"Last Trade: {sorted_trades[-1]['exit_time']}")

def validate_dashboard_format(trades):
    """
    Validate that trades are in correct Dashboard format.
    
    Args:
        trades: List of trade dictionaries
    
    Returns:
        bool: True if valid, False otherwise
    """
    required_fields = ["id", "account_id", "symbol", "side", "quantity", 
                      "price", "close_price", "profit", "entry_time", "exit_time"]
    
    if not trades:
        print("❌ No trades to validate")
        return False
    
    for i, trade in enumerate(trades):
        for field in required_fields:
            if field not in trade:
                print(f"❌ Missing field '{field}' in trade {i}")
                return False
        
        # Validate side values
        if trade['side'] not in ['LONG', 'SHORT']:
            print(f"❌ Invalid side '{trade['side']}' in trade {i}")
            return False
    
    print("✅ All trades are in valid Dashboard format")
    return True

# Main execution
if __name__ == "__main__":
    # File paths
    csv_file = "trading-journal.csv"  # Update this path if needed
    json_file = "trades2.json"
    
    print("Converting Trading Journal CSV to Dashboard Format...")
    print(f"Input file: {csv_file}")
    print(f"Output file: {json_file}")
    
    # Convert CSV to Dashboard format
    dashboard_trades = csv_to_dashboard_format(csv_file, account_id="TRADING_JOURNAL")
    
    if dashboard_trades:
        # Validate the format
        if validate_dashboard_format(dashboard_trades):
            
            # Save to JSON
            save_trades_to_json(dashboard_trades, json_file)
            
            # Print summary
            print_trades_summary(dashboard_trades)
            
            # Show sample trades
            print(f"\n{'='*60}")
            print("SAMPLE TRADES (First 3)")
            print(f"{'='*60}")
            pprint(dashboard_trades[:3])
            
            print(f"\n{'='*60}")
            print("✅ CONVERSION SUCCESSFUL!")
            print(f"{'='*60}")
            print(f"✅ Converted {len(dashboard_trades)} trades from CSV")
            print(f"✅ Saved to {json_file}")
            print("✅ File is ready for Trading Dashboard")
            print("✅ Copy the trades.json file to your Dashboard folder")
            
        else:
            print("❌ Validation failed - please check the data")
    else:
        print("❌ No trades were converted. Please check your CSV file.")

# Quick function for simple conversion
def quick_convert(csv_path="tradingjournal.csv", json_path="trades.json", account="CSV_TRADES"):
    """
    Quick function to convert CSV to JSON with minimal output.
    
    Args:
        csv_path: Path to CSV file
        json_path: Path to output JSON file
        account: Account ID to use
    """
    trades = csv_to_dashboard_format(csv_path, account)
    if trades:
        save_trades_to_json(trades, json_path)
        print(f"✅ Converted {len(trades)} trades: {csv_path} → {json_path}")
        return True
    else:
        print(f"❌ Failed to convert {csv_path}")
        return False