<div align="center">
  <img src="https://images.unsplash.com/photo-1536440136628-849c177e76a1?q=80&w=2025&auto=format&fit=crop" alt="Banner" width="100%" height="250" style="object-fit: cover; border-radius: 10px;">
  
  # 🍿 Netflix-Style Movie Recommendation Engine 🎬

  **An immersive, single-page Streamlit application that breaks the boundaries of traditional dashboards.**
  
  [![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)]()
  [![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)]()
  [![Scikit-Learn](https://img.shields.io/badge/scikit_learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)]()
  [![Pandas](https://img.shields.io/badge/Pandas-2C2D72?style=for-the-badge&logo=pandas&logoColor=white)]()
</div>

---

## 🌟 Overview

This project is a sophisticated **Movie Recommendation System** implemented in Python utilizing Item-Based Collaborative Filtering (Cosine Similarity). 

Where it truly shines is the **Frontend UI**. It completely bypasses standard Streamlit widget limitations by injecting robust HTML, CSS, and cross-origin JavaScript directly into the DOM—resulting in a breathtaking, premium "Netflix-esque" viewing experience.

---

## ✨ Key Features

| Feature | Description |
| :--- | :--- |
| 🎥 **Cinematic Intro** | The app greets users with an authentic, unmuted `mp4` intro video overlay that perfectly fades out when completed. Built with intelligent JS Promises to ensure autoplay! |
| 🌌 **Dynamic Hero Section** | The selected movie dynamically alters the Hero banner background via deterministic hashing against high-quality cinematic placeholder photography. |
| 🎠 **Horizontal Carousels** | Unlike standard vertical layouts, recommendations appear in a sleek, horizontal, smooth-scrolling flexbox gallery representing the Netflix UI. |
| 🪄 **Hover Micro-Interactions** | Recommendation cards dynamically scale up on hover (`transform: scale(1.35)`), revealing deep movie metadata, fake genres, and click action buttons. |
| 💀 **Skeleton Loaders** | Beautiful CSS-only pulse animations provide instant psychological feedback while recommendations generate. |
| 💾 **Client-Side Persistence** | "Like" (♥) and "Save to Picks" (+) interactions are saved locally via `window.localStorage` injected seamlessly into the frontend so clicks feel instantly responsive. |

---

## 🧠 Recommendation Algorithm

The backend recommendation engine logic lives in `recommender.py`:
1. **Data Ingestion**: Parses the standard `ml-latest-small` dataset (Movies & Ratings).
2. **Matrix Pivoting**: Generates a massive User-Item matrix mapped by movie title.
3. **Similarity Calculation**: Employs `sklearn.metrics.pairwise.cosine_similarity` to map Euclidean distances between user preferences.
4. **Threshold Filtering**: Drops poorly rated or obscure movies to ensure premium recommendation outputs.

---

## 🛠️ Installation & Setup

Follow these steps to deploy this application locally:

### 1. Clone the Repository
```bash
git clone https://github.com/TanviKabi1/Movie-Recommendation.git
cd Movie-Recommendation
```

### 2. Install Dependencies
```bash
pip install pandas scikit-learn streamlit
```

### 3. Download the Dataset
We utilize the MovieLens latest-small dataset. A built-in python script is provided to automatically fetch and extract it!
```bash
python dataset_downloader.py
```

### 4. Run the Streamlit Server
```bash
streamlit run app.py
```
> **Note:** If your browser strictly blocks unmuted video autoplay on the very first opening, simply click anywhere and refresh, or let the smart-fallback catch the promise rejection and play the intro silently!

---

## 📂 Project Structure

```text
Movie-Recommendation/
├── app.py                  # Main Streamlit Frontend + Deep CSS/JS Injections
├── recommender.py          # Backend Cosine Similarity Engine
├── dataset_downloader.py   # Utility to fetch MovieLens Data
├── netflix_intro.mp4       # Local video file for the immersive startup sequence
└── data/                   # Auto-generated directory containing ratings.csv & movies.csv
```

---

<div align="center">
  <i>Crafted with ❤️ and code. Let's watch something amazing!</i>
</div>
