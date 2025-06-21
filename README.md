# ✈️ Real-Time Flight Tracking & Delay Analysis

This project is a real-time data pipeline that ingests, processes, stores, and visualizes live global flight data. It showcases a modern data engineering and analytics stack built with open-source tools.

## 📊 Features

- Real-time flight data ingestion from OpenSky API using Python & Kafka
- Data processing with Apache Spark (batch/streaming)
- PostgreSQL as the analytical database
- Interactive dashboards with Apache Superset

## 🧰 Tech Stack

- Apache Kafka (via Confluent images)
- Apache Spark (Bitnami image)
- PostgreSQL
- Apache Superset
- Docker & Docker Compose
- Python

## 📁 Folder Structure

```
flight-data-pipeline/
├── docker-compose.yml
├── flight_producer.py
├── insert_parquet_to_postgres.py
├── spark-app/
│   └── output/         # Parquet files
├── superset/           # Superset volume (dashboards, charts)
├── postgres_data/      # PostgreSQL volume
├── dashboards/         # Exported dashboard images
```

## 🚀 How to Run

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/flight-data-pipeline.git
   cd flight-data-pipeline
   ```

2. **Start All Services**
   ```bash
   docker-compose up
   ```

3. **Run the Flight Data Producer**
   This script fetches live flight data and pushes it to Kafka.
   ```bash
   python flight_producer.py
   ```

4. **Process and Store with Spark**
   Insert the cleaned Parquet data into PostgreSQL.
   ```bash
   docker exec -it flight-data-pipeline-spark \
     spark-submit /opt/bitnami/spark-app/insert_parquet_to_postgres.py
   ```

## 📷 Sample Dashboards

Dashboards are saved as static images in the `Images` folder.  
They include:

- Flights by Country of Origin  
- Altitude vs Velocity  
- Top Active Aircrafts by Callsign  

## 📦 Data Source

- [OpenSky Network API](https://opensky-network.org/): Provides real-time air traffic data.

## 🧑‍💻 Author

**Zakaria Alaimia**  
Data & BI Enthusiast | Final Year Engineering Student  
[LinkedIn](https://www.linkedin.com/in/zakaria-alaimia-274231156/)  
[GitHub](https://github.com/zak-attack-1)

## 📜 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

---

Feel free to ⭐️ the repo if you find it useful!



