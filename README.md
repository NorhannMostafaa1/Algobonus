# Cairo Traffic Intelligence Lab

Cairo Traffic Intelligence Lab is a traffic forecasting and route analysis project focused on Cairo road segments and urban districts. The project combines machine learning traffic prediction with graph-based pathfinding to compare how Dijkstra and A* behave on the same congestion-weighted road network.

## Project Overview

The app visualizes a modeled Cairo traffic network and lets the user:
- Select a traffic scenario such as Morning Peak, Afternoon, Evening Peak, or Night.
- Choose a start point and destination.
- Compare Dijkstra and A* side by side on predicted travel costs.
- Explore congestion hotspots and suggested new road connections.

The interface is built as a lightweight web app using HTML, CSS, and JavaScript, while the data generation pipeline uses Python and scikit-learn.

## Main Features

- Interactive Cairo network map with districts and facilities.
- Congestion-based edge coloring for quick visual analysis.
- Side-by-side algorithm race board for Dijkstra and A*.
- Machine learning predictions generated with `RandomForestRegressor`.
- Forecast highlights for the most stressed road segments.
- Exported app data in both JavaScript and JSON formats.

## Model Information

The generated project data currently reports:
- City: Cairo
- Dataset source: CSE112 Project Provided Data PDF
- Model: `RandomForestRegressor (scikit-learn)`
- Mean Absolute Error: `96.86 veh/h`
- R2 Score: `0.976`
- Training rows: `1512`
- Test rows: `303`

## Project Structure

```text
New project/
|-- index.html
|-- styles.css
|-- app.js
|-- data/
|   `-- generated/
|       |-- app-data.js
|       `-- app-data.json
`-- scripts/
    `-- train_and_export.py
```

## How To Run

### Option 1: Open the frontend directly

Because this project is a static web app, you can open `index.html` in a browser to view the interface.

### Option 2: Use a local server

If you prefer serving it locally, run a simple static server from the project folder. For example:

```powershell
python -m http.server 8000
```

Then open:

```text
http://localhost:8000
```

## How To Regenerate The Data

The file `scripts/train_and_export.py` rebuilds the generated traffic data used by the frontend.

Run it from the project root after installing the required Python packages:

```powershell
python scripts/train_and_export.py
```

This will update:
- `data/generated/app-data.js`
- `data/generated/app-data.json`

## Technologies Used

- HTML5
- CSS3
- JavaScript
- Python
- pandas
- numpy
- scikit-learn

## Purpose

This project is useful as an academic or portfolio demonstration of how machine learning and classical graph algorithms can work together in a smart mobility context. It shows both predicted congestion behavior and pathfinding decisions in a clear, visual format.
