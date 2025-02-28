from fastapi import FastAPI
import sqlite3
import pandas as pd

# Initialize FastAPI app
app = FastAPI()

# Load pincode data
pincode_data = pd.read_parquet(r"C:\Users\user\Downloads\pincode_coordinates.parquet")  # Update path if needed

@app.get("/station_info/")
def get_station_info(station_code: str):
    try:
        # Connect to SQLite to get the Pincode
        conn = sqlite3.connect(r"C:\Users\user\Downloads\pincode_station.db")  # Update path
        query = "SELECT * FROM Pincode_Station_Code WHERE `STATION\nCODE` = ?"
        station_df = pd.read_sql(query, conn, params=(station_code,))
        conn.close()

        if station_df.empty:
            return {"error": "Station code not found"}

        # Extract Pincode
        pincode = station_df["PIN Code"].iloc[0]

        # Get location info from pincode_coordinates.parquet
        location_info = pincode_data[pincode_data["PIN Code"] == pincode]

        if location_info.empty:
            return {"state_name": None, "district_name": None, "pincode": pincode}

        # No state or district available, return None
        return {"state_name": None, "district_name": None, "pincode": pincode}

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)