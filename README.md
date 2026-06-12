# 🎬 Movie Recommendation System

A content-based movie recommendation web app built with **Python + Flask**, powered by the **TMDB API** for real-time poster fetching.

---

## ✨ Features

- 🔍 Search any movie with autocomplete suggestions
- 🎯 Get 5 similar movie recommendations instantly
- 🖼️ Live poster images fetched from TMDB
- ⚡ Fast cosine-similarity-based recommendation engine
- 📱 Responsive, modern dark UI

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+, Flask |
| ML Model | scikit-learn (TF-IDF + Cosine Similarity) |
| Data | TMDB 5000 Movie Dataset (Kaggle) |
| Poster API | [TMDB API](https://developer.themoviedb.org/) |
| Frontend | HTML, CSS, Vanilla JS |

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/movies-recommendation-system.git
cd movies-recommendation-system
```

### 2. Create & Activate a Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Your TMDB API Key

Copy the example env file and add your key:

```bash
cp .env.example .env
```

Edit `.env`:

```
TMDB_API_KEY=your_tmdb_api_key_here
```

> 🔑 Get a free TMDB API key at: https://developer.themoviedb.org/docs/getting-started

### 5. Download the Dataset

Download from Kaggle: [TMDB 5000 Movie Dataset](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata)

Place these two files in the project root:
- `tmdb_5000_movies.csv`
- `tmdb_5000_credits.csv`

### 6. Generate the Model Files

Run the Jupyter notebook to generate `movies.pkl` and `similarity.pkl`:

```bash
jupyter notebook model.ipynb
```

Run all cells. This will create the two `.pkl` files needed to run the app.

### 7. Run the App

```bash
python app.py
```

Open your browser at: **http://127.0.0.1:5000**

---

## 📂 Project Structure

```
movies-recommendation-system/
├── app.py                  # Flask web server & recommendation logic
├── model.ipynb             # Jupyter notebook to train & save the model
├── templates/
│   └── index.html          # Frontend UI
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

> **Note:** `movies.pkl`, `similarity.pkl`, and the CSV files are excluded from version control because they are too large. Generate them locally using `model.ipynb`.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serves the main UI |
| `GET` | `/autocomplete?q=<query>` | Returns up to 8 movie title suggestions |
| `POST` | `/recommend` | Returns 5 recommended movies |

### `/recommend` Request Body

```json
{ "title": "Avatar" }
```

### `/recommend` Response

```json
{
  "matched_title": "Avatar",
  "recommendations": [
    {
      "title": "Guardians of the Galaxy",
      "poster": "https://image.tmdb.org/t/p/w500/...",
      "tmdb_id": 118340
    }
  ]
}
```

---

## ⚠️ Important Notes

- The `similarity.pkl` file is ~176 MB and is **not stored in Git**. You must generate it locally.
- Never commit your `.env` file — it contains your private API key.
- The TMDB API is used only for fetching poster images; the recommendation logic runs fully offline.

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
