# Cairo Traffic Intelligence Lab

This project turns the provided Cairo transport dataset into two connected experiences:

1. A `scikit-learn` traffic forecasting pipeline that predicts road-level congestion by time of day.
2. A browser dashboard that visualizes those forecasts and runs a side-by-side Dijkstra vs A* route race on the same weighted graph.

## What's included

- [scripts/train_and_export.py](C:\Users\USER\OneDrive\Documents\New project\scripts\train_and_export.py) encodes the PDF dataset, trains a `RandomForestRegressor`, and exports frontend-ready data.
- [index.html](C:\Users\USER\OneDrive\Documents\New project\index.html), [styles.css](C:\Users\USER\OneDrive\Documents\New project\styles.css), and [app.js](C:\Users\USER\OneDrive\Documents\New project\app.js) provide the interactive visualizer.
- [data/generated/app-data.js](C:\Users\USER\OneDrive\Documents\New project\data\generated\app-data.js) is the generated bundle consumed by the UI.

## Run it

1. Regenerate the ML forecast data:

```powershell
C:\Users\USER\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts\train_and_export.py
```

2. Open the dashboard in a browser by opening [index.html](C:\Users\USER\OneDrive\Documents\New project\index.html).

## Modeling note

The source PDF provides four temporal traffic observations per road segment. The training script uses those baseline measurements as the core supervision signal, then creates small day-level temporal variations around them so the `scikit-learn` model can learn a smoother forecasting surface for scenario prediction.
