from __future__ import annotations

import os
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

load_dotenv()  # Load environment variables from .env file

BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)

TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "")
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
PLACEHOLDER_POSTER = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='300'%3E%3Crect fill='%230d111a' width='200' height='300'/%3E%3Ctext x='50%25' y='50%25' font-family='Arial' font-size='14' fill='%23a1a7b5' text-anchor='middle' dy='.3em'%3ENo Poster%3C/text%3E%3C/svg%3E"


def load_assets() -> tuple[pd.DataFrame, np.ndarray]:
    movies_path = BASE_DIR / "movies.pkl"
    similarity_path = BASE_DIR / "similarity.pkl"

    with movies_path.open("rb") as movies_file:
        movies_df = pickle.load(movies_file)

    with similarity_path.open("rb") as similarity_file:
        similarity_matrix = pickle.load(similarity_file)

    if not isinstance(movies_df, pd.DataFrame):
        movies_df = pd.DataFrame(movies_df)

    title_column = next(
        (column for column in ("title", "Title", "movie_title") if column in movies_df.columns),
        None,
    )
    if not title_column:
        raise ValueError("movies.pkl must include a title column.")

    if title_column != "title":
        movies_df = movies_df.rename(columns={title_column: "title"})

    similarity_array = np.array(similarity_matrix)
    return movies_df, similarity_array


movies, similarity = load_assets()
movies["title"] = movies["title"].fillna("").astype(str)
movies["title_lower"] = movies["title"].str.lower()
title_to_index = {title: idx for idx, title in enumerate(movies["title_lower"])}


def fetch_poster_url(movie_id: int | float | None, movie_title: str) -> str:
    if movie_id is None or pd.isna(movie_id):
        app.logger.warning("Missing movie_id for '%s'. Using placeholder poster.", movie_title)
        return PLACEHOLDER_POSTER

    try:
        tmdb_id = int(movie_id)
    except (TypeError, ValueError) as exc:
        app.logger.warning(
            "Invalid movie_id '%s' for '%s': %s. Using placeholder poster.",
            movie_id,
            movie_title,
            exc,
        )
        return PLACEHOLDER_POSTER

    app.logger.info("Fetching poster for id=%s ('%s').", tmdb_id, movie_title)
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={TMDB_API_KEY}"
    try:
        response = requests.get(url, timeout=5)
    except requests.RequestException as exc:
        app.logger.warning(
            "TMDB request failed for id=%s ('%s'): %s. Using placeholder poster.",
            tmdb_id,
            movie_title,
            exc,
        )
        return PLACEHOLDER_POSTER

    if response.status_code != 200:
        app.logger.warning(
            "TMDB response %s for id=%s ('%s'). Using placeholder poster.",
            response.status_code,
            tmdb_id,
            movie_title,
        )
        return PLACEHOLDER_POSTER

    try:
        data = response.json()
    except ValueError as exc:
        app.logger.warning(
            "TMDB JSON parse failed for id=%s ('%s'): %s. Using placeholder poster.",
            tmdb_id,
            movie_title,
            exc,
        )
        return PLACEHOLDER_POSTER

    poster_path = data.get("poster_path")
    if not poster_path:
        app.logger.info("No poster_path for id=%s ('%s'). Using placeholder poster.", tmdb_id, movie_title)
        return PLACEHOLDER_POSTER

    poster_url = f"{TMDB_IMAGE_BASE_URL}{poster_path}"
    app.logger.info("Poster resolved for id=%s ('%s').", tmdb_id, movie_title)
    return poster_url


def get_recommendations(
    movie_title: str, top_n: int = 5
) -> tuple[list[dict[str, str | int | None]], str | None]:
    normalized_title = movie_title.strip().lower()
    if not normalized_title:
        return [], None

    matched_title_lower = normalized_title
    if matched_title_lower not in title_to_index:
        matches = movies[movies["title_lower"].str.startswith(normalized_title, na=False)]
        if matches.empty:
            return [], None
        matched_title_lower = matches.iloc[0]["title_lower"]

    movie_index = title_to_index[matched_title_lower]
    if movie_index >= similarity.shape[0]:
        return [], None

    distances = similarity[movie_index]

    ranked = sorted(
        enumerate(distances),
        key=lambda item: item[1],
        reverse=True,
    )

    recommendations = []
    for idx, _score in ranked:
        if idx == movie_index:
            continue
        title = movies.iloc[idx]["title"]
        movie_id = movies.iloc[idx]["movie_id"]
        poster_url = fetch_poster_url(movie_id, title)
        tmdb_id: int | None
        try:
            tmdb_id = int(movie_id) if not pd.isna(movie_id) else None
        except (TypeError, ValueError):
            tmdb_id = None
        recommendations.append(
            {
                "title": title,
                "poster": poster_url,
                "tmdb_id": tmdb_id,
            }
        )
        if len(recommendations) >= top_n:
            break

    matched_title = movies.iloc[movie_index]["title"]
    app.logger.info(
        "Returning %s recommendations for '%s'.",
        len(recommendations),
        matched_title,
    )
    return recommendations, matched_title


@app.get("/")
def index() -> str:
    return render_template("index.html")


@app.get("/autocomplete")
def autocomplete() -> tuple[str, int] | tuple[dict[str, list[str]], int]:
    query = request.args.get("q", "").strip().lower()
    if not query:
        return jsonify({"suggestions": []}), 200

    matches = movies[movies["title_lower"].str.startswith(query, na=False)]
    suggestions = matches["title"].head(8).tolist()
    return jsonify({"suggestions": suggestions}), 200


@app.post("/recommend")
def recommend() -> tuple[str, int] | tuple[
    dict[str, list[dict[str, str | int | None]] | str], int
]:
    payload = request.get_json(silent=True) or {}
    movie_title = str(payload.get("title", "")).strip()

    recommendations, matched_title = get_recommendations(movie_title)
    if not recommendations:
        return (
            jsonify({"error": "Movie not found in our database."}),
            404,
        )

    return (
        jsonify({"recommendations": recommendations, "matched_title": matched_title}),
        200,
    )


if __name__ == "__main__":
    app.run(debug=True)
