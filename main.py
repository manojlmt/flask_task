from flask import Flask, request, jsonify
import sqlite3
import pandas as pd

app = Flask(__name__)

# Load your data into a DataFrame globally (or consider moving this inside the route if it changes frequently)
df = pd.read_excel('C:\project\Flask\data.xls')

# Ensure numeric columns are converted to float
df['OIL'] = pd.to_numeric(df['OIL'], errors='coerce')
df['GAS'] = pd.to_numeric(df['GAS'], errors='coerce')
df['BRINE'] = pd.to_numeric(df['BRINE'], errors='coerce')

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('well_data.db')
cursor = conn.cursor()

# Create a table to store the data if it doesn't already exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS AnnualWellData (
    API_WELL_NUMBER INTEGER PRIMARY KEY,
    OIL_SUM REAL,
    GAS_SUM REAL,
    BRINE_SUM REAL
)
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

def calculate_sums(well):
    # Find the row(s) where 'API WELL NUMBER' matches the desired value
    result = df[df['API WELL  NUMBER'] == well]

    # Calculate the sum of the 'OIL', 'GAS', and 'BRINE' columns
    oil_sum = result['OIL'].sum() if not result.empty else 0
    gas_sum = result['GAS'].sum() if not result.empty else 0
    brine_sum = result['BRINE'].sum() if not result.empty else 0

    return oil_sum, gas_sum, brine_sum

# Define the route for the GET request
@app.route('/data', methods=['GET'])
def data():
    well = request.args.get('well', type=int)  # Get the 'well' parameter from the URL
    if well is None:
        return jsonify({"error": "No well number provided."}), 400

    # Calculate the sums for the requested well number
    oil_sum, gas_sum, brine_sum = calculate_sums(well)

    # Connect to SQLite database
    conn = sqlite3.connect('well_data.db')
    cursor = conn.cursor()

    # Insert or replace the data into the table
    cursor.execute('''
    INSERT OR REPLACE INTO AnnualWellData (API_WELL_NUMBER, OIL_SUM, GAS_SUM, BRINE_SUM)
    VALUES (?, ?, ?, ?)
    ''', (well, float(oil_sum), float(gas_sum), float(brine_sum)))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    # Return the sums as a JSON response
    return jsonify({
        "oil": float(oil_sum),
        "gas": float(gas_sum),
        "brine": float(brine_sum)
    })

# Run the app on port 8080
if __name__ == '__main__':
    app.run(port=8080)
