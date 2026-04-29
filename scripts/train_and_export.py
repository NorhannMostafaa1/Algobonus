from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_JS = ROOT / "data" / "generated" / "app-data.js"
OUTPUT_JSON = ROOT / "data" / "generated" / "app-data.json"


DISTRICTS = [
    {"id": "1", "name": "Maadi", "population": 250000, "type": "Residential", "x": 31.25, "y": 29.96},
    {"id": "2", "name": "Nasr City", "population": 500000, "type": "Mixed", "x": 31.34, "y": 30.06},
    {"id": "3", "name": "Downtown Cairo", "population": 100000, "type": "Business", "x": 31.24, "y": 30.04},
    {"id": "4", "name": "New Cairo", "population": 300000, "type": "Residential", "x": 31.47, "y": 30.03},
    {"id": "5", "name": "Heliopolis", "population": 200000, "type": "Mixed", "x": 31.32, "y": 30.09},
    {"id": "6", "name": "Zamalek", "population": 50000, "type": "Residential", "x": 31.22, "y": 30.06},
    {"id": "7", "name": "6th October City", "population": 400000, "type": "Mixed", "x": 30.98, "y": 29.93},
    {"id": "8", "name": "Giza", "population": 550000, "type": "Mixed", "x": 31.21, "y": 29.99},
    {"id": "9", "name": "Mohandessin", "population": 180000, "type": "Business", "x": 31.20, "y": 30.05},
    {"id": "10", "name": "Dokki", "population": 220000, "type": "Mixed", "x": 31.21, "y": 30.03},
    {"id": "11", "name": "Shubra", "population": 450000, "type": "Residential", "x": 31.24, "y": 30.11},
    {"id": "12", "name": "Helwan", "population": 350000, "type": "Industrial", "x": 31.33, "y": 29.85},
    {"id": "13", "name": "New Administrative Capital", "population": 50000, "type": "Government", "x": 31.80, "y": 30.02},
    {"id": "14", "name": "Al Rehab", "population": 120000, "type": "Residential", "x": 31.49, "y": 30.06},
    {"id": "15", "name": "Sheikh Zayed", "population": 150000, "type": "Residential", "x": 30.94, "y": 30.01},
]


FACILITIES = [
    {"id": "F1", "name": "Cairo International Airport", "type": "Airport", "x": 31.41, "y": 30.11},
    {"id": "F2", "name": "Ramses Railway Station", "type": "Transit Hub", "x": 31.25, "y": 30.06},
    {"id": "F3", "name": "Cairo University", "type": "Education", "x": 31.21, "y": 30.03},
    {"id": "F4", "name": "Al-Azhar University", "type": "Education", "x": 31.26, "y": 30.05},
    {"id": "F5", "name": "Egyptian Museum", "type": "Tourism", "x": 31.23, "y": 30.05},
    {"id": "F6", "name": "Cairo International Stadium", "type": "Sports", "x": 31.30, "y": 30.07},
    {"id": "F7", "name": "Smart Village", "type": "Business", "x": 30.97, "y": 30.07},
    {"id": "F8", "name": "Cairo Festival City", "type": "Commercial", "x": 31.40, "y": 30.03},
    {"id": "F9", "name": "Qasr El Aini Hospital", "type": "Medical", "x": 31.23, "y": 30.03},
    {"id": "F10", "name": "Maadi Military Hospital", "type": "Medical", "x": 31.25, "y": 29.95},
]


EXISTING_ROADS = [
    ("1", "3", 8.5, 3000, 7),
    ("1", "8", 6.2, 2500, 6),
    ("2", "3", 5.9, 2800, 8),
    ("2", "5", 4.0, 3200, 9),
    ("3", "5", 6.1, 3500, 7),
    ("3", "6", 3.2, 2000, 8),
    ("3", "9", 4.5, 2600, 6),
    ("3", "10", 3.8, 2400, 7),
    ("4", "2", 15.2, 3800, 9),
    ("4", "14", 5.3, 3000, 10),
    ("5", "11", 7.9, 3100, 7),
    ("6", "9", 2.2, 1800, 8),
    ("7", "8", 24.5, 3500, 8),
    ("7", "15", 9.8, 3000, 9),
    ("8", "10", 3.3, 2200, 7),
    ("8", "12", 14.8, 2600, 5),
    ("9", "10", 2.1, 1900, 7),
    ("10", "11", 8.7, 2400, 6),
    ("11", "F2", 3.6, 2200, 7),
    ("12", "1", 12.7, 2800, 6),
    ("13", "4", 45.0, 4000, 10),
    ("14", "13", 35.5, 3800, 9),
    ("15", "7", 9.8, 3000, 9),
    ("F1", "5", 7.5, 3500, 9),
    ("F1", "2", 9.2, 3200, 8),
    ("F2", "3", 2.5, 2000, 7),
    ("F7", "15", 8.3, 2800, 8),
    ("F8", "4", 6.1, 3000, 9),
]


POTENTIAL_ROADS = [
    ("1", "4", 22.8, 4000, 450),
    ("1", "14", 25.3, 3800, 500),
    ("2", "13", 48.2, 4500, 950),
    ("3", "13", 56.7, 4500, 1100),
    ("5", "4", 16.8, 3500, 320),
    ("6", "8", 7.5, 2500, 150),
    ("7", "13", 82.3, 4000, 1600),
    ("9", "11", 6.9, 2800, 140),
    ("10", "F7", 27.4, 3200, 550),
    ("11", "13", 62.1, 4200, 1250),
    ("12", "14", 30.5, 3600, 610),
    ("14", "5", 18.2, 3300, 360),
    ("15", "9", 22.7, 3000, 450),
    ("F1", "13", 40.2, 4000, 800),
    ("F7", "9", 26.8, 3200, 540),
]


TRAFFIC_PATTERNS = {
    "1-3": {"Morning Peak": 2800, "Afternoon": 1500, "Evening Peak": 2600, "Night": 800},
    "1-8": {"Morning Peak": 2200, "Afternoon": 1200, "Evening Peak": 2100, "Night": 600},
    "2-3": {"Morning Peak": 2700, "Afternoon": 1400, "Evening Peak": 2500, "Night": 700},
    "2-5": {"Morning Peak": 3000, "Afternoon": 1600, "Evening Peak": 2800, "Night": 650},
    "3-5": {"Morning Peak": 3200, "Afternoon": 1700, "Evening Peak": 3100, "Night": 800},
    "3-6": {"Morning Peak": 1800, "Afternoon": 1400, "Evening Peak": 1900, "Night": 500},
    "3-9": {"Morning Peak": 2400, "Afternoon": 1300, "Evening Peak": 2200, "Night": 550},
    "3-10": {"Morning Peak": 2300, "Afternoon": 1200, "Evening Peak": 2100, "Night": 500},
    "4-2": {"Morning Peak": 3600, "Afternoon": 1800, "Evening Peak": 3300, "Night": 750},
    "4-14": {"Morning Peak": 2800, "Afternoon": 1600, "Evening Peak": 2600, "Night": 600},
    "5-11": {"Morning Peak": 2900, "Afternoon": 1500, "Evening Peak": 2700, "Night": 650},
    "6-9": {"Morning Peak": 1700, "Afternoon": 1300, "Evening Peak": 1800, "Night": 450},
    "7-8": {"Morning Peak": 3200, "Afternoon": 1700, "Evening Peak": 3000, "Night": 700},
    "7-15": {"Morning Peak": 2800, "Afternoon": 1500, "Evening Peak": 2600, "Night": 600},
    "8-10": {"Morning Peak": 2000, "Afternoon": 1100, "Evening Peak": 1900, "Night": 450},
    "8-12": {"Morning Peak": 2400, "Afternoon": 1300, "Evening Peak": 2200, "Night": 500},
    "9-10": {"Morning Peak": 1800, "Afternoon": 1200, "Evening Peak": 1700, "Night": 400},
    "10-11": {"Morning Peak": 2200, "Afternoon": 1300, "Evening Peak": 2100, "Night": 500},
    "11-F2": {"Morning Peak": 2100, "Afternoon": 1200, "Evening Peak": 2000, "Night": 450},
    "12-1": {"Morning Peak": 2600, "Afternoon": 1400, "Evening Peak": 2400, "Night": 550},
    "13-4": {"Morning Peak": 3800, "Afternoon": 2000, "Evening Peak": 3500, "Night": 800},
    "14-13": {"Morning Peak": 3600, "Afternoon": 1900, "Evening Peak": 3300, "Night": 750},
    "15-7": {"Morning Peak": 2800, "Afternoon": 1500, "Evening Peak": 2600, "Night": 600},
    "F1-5": {"Morning Peak": 3300, "Afternoon": 2200, "Evening Peak": 3100, "Night": 1200},
    "F1-2": {"Morning Peak": 3000, "Afternoon": 2000, "Evening Peak": 2800, "Night": 1100},
    "F2-3": {"Morning Peak": 1900, "Afternoon": 1600, "Evening Peak": 1800, "Night": 900},
    "F7-15": {"Morning Peak": 2600, "Afternoon": 1500, "Evening Peak": 2400, "Night": 550},
    "F8-4": {"Morning Peak": 2800, "Afternoon": 1600, "Evening Peak": 2600, "Night": 600},
}


PERIOD_META = {
    "Morning Peak": {"hour": 8, "temperature_c": 24, "event_factor": 1.12},
    "Afternoon": {"hour": 14, "temperature_c": 30, "event_factor": 0.95},
    "Evening Peak": {"hour": 18, "temperature_c": 27, "event_factor": 1.08},
    "Night": {"hour": 23, "temperature_c": 21, "event_factor": 0.55},
}


NODE_LOOKUP = {node["id"]: node for node in DISTRICTS + FACILITIES}


def node_sort_key(node_id: str):
    if node_id.startswith("F"):
        return (1, int(node_id[1:]))
    return (0, int(node_id))


def road_key(from_id: str, to_id: str) -> str:
    return "-".join(sorted([from_id, to_id], key=node_sort_key))


def population_for(node_id: str) -> int:
    node = NODE_LOOKUP[node_id]
    return node.get("population", 0)


def kind_for(node_id: str) -> str:
    node = NODE_LOOKUP[node_id]
    return node["type"]


def build_roads():
    roads = []
    degrees: dict[str, int] = {}
    seen_road_ids: set[str] = set()

    for from_id, to_id, distance, capacity, condition in EXISTING_ROADS:
        normalized_id = road_key(from_id, to_id)
        if normalized_id in seen_road_ids:
            continue
        seen_road_ids.add(normalized_id)
        degrees[from_id] = degrees.get(from_id, 0) + 1
        degrees[to_id] = degrees.get(to_id, 0) + 1
        roads.append(
            {
                "id": normalized_id,
                "from": from_id,
                "to": to_id,
                "distance_km": distance,
                "capacity_vph": capacity,
                "condition": condition,
            }
        )

    for road in roads:
        road["degree_sum"] = degrees.get(road["from"], 0) + degrees.get(road["to"], 0)
        road["from_population"] = population_for(road["from"])
        road["to_population"] = population_for(road["to"])
        road["population_sum"] = road["from_population"] + road["to_population"]
        road["from_type"] = kind_for(road["from"])
        road["to_type"] = kind_for(road["to"])

    return roads


def build_training_frame(roads: list[dict]) -> pd.DataFrame:
    rows = []
    rng = np.random.default_rng(42)

    for road in roads:
        patterns = (
            TRAFFIC_PATTERNS.get(road["id"])
            or TRAFFIC_PATTERNS.get(f"{road['from']}-{road['to']}")
            or TRAFFIC_PATTERNS.get(f"{road['to']}-{road['from']}")
        )
        for period_name, observed_flow in patterns.items():
            base = PERIOD_META[period_name]
            for sample_idx in range(14):
                day_of_week = sample_idx % 7
                weekend = 1 if day_of_week in (4, 5) else 0
                weather_noise = rng.normal(0, 1.2)
                incident_factor = rng.uniform(0.95, 1.08)
                seasonal_factor = 1 + 0.015 * np.sin((sample_idx / 14) * np.pi * 2)
                weekend_factor = 0.91 if weekend else 1.0
                congestion_shift = rng.normal(0, 0.04)
                synthetic_target = observed_flow * weekend_factor * seasonal_factor * incident_factor * (1 + congestion_shift)
                rows.append(
                    {
                        "road_id": road["id"],
                        "from_id": road["from"],
                        "to_id": road["to"],
                        "distance_km": road["distance_km"],
                        "capacity_vph": road["capacity_vph"],
                        "condition": road["condition"],
                        "degree_sum": road["degree_sum"],
                        "population_sum": road["population_sum"],
                        "from_type": road["from_type"],
                        "to_type": road["to_type"],
                        "period_name": period_name,
                        "hour": base["hour"],
                        "sin_hour": np.sin((2 * np.pi * base["hour"]) / 24),
                        "cos_hour": np.cos((2 * np.pi * base["hour"]) / 24),
                        "weekend": weekend,
                        "day_of_week": day_of_week,
                        "temperature_c": base["temperature_c"] + weather_noise,
                        "event_factor": base["event_factor"],
                        "flow_vph": max(250, synthetic_target),
                    }
                )

    return pd.DataFrame(rows)


def train_model(training_frame: pd.DataFrame):
    feature_columns = [
        "distance_km",
        "capacity_vph",
        "condition",
        "degree_sum",
        "population_sum",
        "hour",
        "sin_hour",
        "cos_hour",
        "weekend",
        "day_of_week",
        "temperature_c",
        "event_factor",
        "from_type",
        "to_type",
        "period_name",
    ]
    X = training_frame[feature_columns]
    y = training_frame["flow_vph"]

    numeric_columns = [
        "distance_km",
        "capacity_vph",
        "condition",
        "degree_sum",
        "population_sum",
        "hour",
        "sin_hour",
        "cos_hour",
        "weekend",
        "day_of_week",
        "temperature_c",
        "event_factor",
    ]
    categorical_columns = ["from_type", "to_type", "period_name"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", Pipeline([("imputer", SimpleImputer(strategy="median"))]), numeric_columns),
            (
                "cat",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("encoder", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical_columns,
            ),
        ]
    )

    model = Pipeline(
        steps=[
            ("prep", preprocessor),
            (
                "rf",
                RandomForestRegressor(
                    n_estimators=260,
                    max_depth=12,
                    min_samples_leaf=2,
                    random_state=42,
                ),
            ),
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    metrics = {
        "mae": round(float(mean_absolute_error(y_test, predictions)), 2),
        "r2": round(float(r2_score(y_test, predictions)), 3),
        "training_rows": int(len(training_frame)),
        "test_rows": int(len(X_test)),
    }
    return model, feature_columns, metrics


def predict_scenarios(model, roads: list[dict]) -> dict[str, list[dict]]:
    scenarios = {
        "Morning Peak": {"hour": 8, "temperature_c": 25, "event_factor": 1.11, "weekend": 0, "day_of_week": 2},
        "Afternoon": {"hour": 14, "temperature_c": 31, "event_factor": 0.96, "weekend": 0, "day_of_week": 2},
        "Evening Peak": {"hour": 18, "temperature_c": 28, "event_factor": 1.07, "weekend": 0, "day_of_week": 2},
        "Night": {"hour": 23, "temperature_c": 22, "event_factor": 0.58, "weekend": 0, "day_of_week": 2},
        "Next Morning Forecast": {"hour": 8, "temperature_c": 27, "event_factor": 1.18, "weekend": 0, "day_of_week": 3},
    }

    output: dict[str, list[dict]] = {}
    for scenario_name, meta in scenarios.items():
        rows = []
        for road in roads:
            rows.append(
                {
                    "distance_km": road["distance_km"],
                    "capacity_vph": road["capacity_vph"],
                    "condition": road["condition"],
                    "degree_sum": road["degree_sum"],
                    "population_sum": road["population_sum"],
                    "hour": meta["hour"],
                    "sin_hour": np.sin((2 * np.pi * meta["hour"]) / 24),
                    "cos_hour": np.cos((2 * np.pi * meta["hour"]) / 24),
                    "weekend": meta["weekend"],
                    "day_of_week": meta["day_of_week"],
                    "temperature_c": meta["temperature_c"],
                    "event_factor": meta["event_factor"],
                    "from_type": road["from_type"],
                    "to_type": road["to_type"],
                    "period_name": "Morning Peak" if scenario_name == "Next Morning Forecast" else scenario_name,
                    "road_id": road["id"],
                    "from_id": road["from"],
                    "to_id": road["to"],
                }
            )
        frame = pd.DataFrame(rows)
        predicted = model.predict(frame.drop(columns=["road_id", "from_id", "to_id"]))
        result = []
        for index, road in enumerate(rows):
            capacity = road["capacity_vph"]
            flow = max(250, float(predicted[index]))
            congestion_ratio = flow / capacity
            result.append(
                {
                    "road_id": road["road_id"],
                    "from_id": road["from_id"],
                    "to_id": road["to_id"],
                    "predicted_flow_vph": round(flow, 1),
                    "capacity_vph": capacity,
                    "congestion_ratio": round(congestion_ratio, 3),
                    "travel_cost": round(
                        (frame.iloc[index]["distance_km"] / 32)
                        * (1 + max(0, congestion_ratio - 0.65) * 2.1 + (10 - frame.iloc[index]["condition"]) * 0.03),
                        3,
                    ),
                }
            )
        output[scenario_name] = result
    return output


def recommend_new_roads(predictions_by_scenario: dict[str, list[dict]]) -> list[dict]:
    next_morning = {item["road_id"]: item for item in predictions_by_scenario["Next Morning Forecast"]}
    stressed_road_ids = sorted(next_morning, key=lambda key: next_morning[key]["congestion_ratio"], reverse=True)[:8]
    stressed_nodes = set()
    for road_id in stressed_road_ids:
        stressed_nodes.update(road_id.split("-"))

    recommendations = []
    for from_id, to_id, distance, capacity, cost in POTENTIAL_ROADS:
        stress_bonus = 1.25 if from_id in stressed_nodes or to_id in stressed_nodes else 0.85
        district_weight = (population_for(from_id) + population_for(to_id) + 1) / 300000
        score = (capacity / cost) * stress_bonus * district_weight * max(1, 18 / distance)
        recommendations.append(
            {
                "from_id": from_id,
                "to_id": to_id,
                "road_id": road_key(from_id, to_id),
                "distance_km": distance,
                "estimated_capacity_vph": capacity,
                "construction_cost_million_egp": cost,
                "score": round(score, 3),
            }
        )
    return sorted(recommendations, key=lambda item: item["score"], reverse=True)[:5]


def export_bundle():
    roads = build_roads()
    training_frame = build_training_frame(roads)
    model, _, metrics = train_model(training_frame)
    predictions = predict_scenarios(model, roads)
    top_hotspots = sorted(
        predictions["Next Morning Forecast"],
        key=lambda item: item["congestion_ratio"],
        reverse=True,
    )[:6]

    bundle = {
        "metadata": {
            "city": "Cairo",
            "dataset_source": "CSE112 Project Provided Data PDF",
            "model": "RandomForestRegressor (scikit-learn)",
            "metrics": metrics,
        },
        "nodes": [
            {
                "id": node["id"],
                "name": node["name"],
                "type": node["type"],
                "population": node.get("population", 0),
                "x": node["x"],
                "y": node["y"],
            }
            for node in DISTRICTS + FACILITIES
        ],
        "roads": roads,
        "predictions": predictions,
        "hotspots": top_hotspots,
        "recommended_new_roads": recommend_new_roads(predictions),
    }

    OUTPUT_JSON.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    OUTPUT_JS.write_text(f"window.APP_DATA = {json.dumps(bundle, indent=2)};\n", encoding="utf-8")
    print(f"Wrote {OUTPUT_JSON}")
    print(f"Wrote {OUTPUT_JS}")
    print(json.dumps(bundle["metadata"], indent=2))


if __name__ == "__main__":
    export_bundle()
