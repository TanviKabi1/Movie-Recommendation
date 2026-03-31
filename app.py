import streamlit as st
import pandas as pd
from recommender import load_data, build_similarity_matrix, get_recommendations
import os

st.set_page_config(page_title="Movie Recommender", page_icon="🍿", layout="wide")

# Check if data directory exists
if not os.path.exists(os.path.join("data", "ml-latest-small", "ratings.csv")):
    st.error("Dataset not found. Please run `python dataset_downloader.py` first.")
    st.stop()

@st.cache_data
def load_and_prepare_data():
    movies, ratings = load_data()
    item_similarity_df = build_similarity_matrix(movies, ratings, min_ratings=20)
    return movies, item_similarity_df

# Handle intro animation logic using Streamlit session state and CSS animations
if 'intro_played' not in st.session_state:
    import base64
    import streamlit.components.v1 as components
    
    video_path = "netflix_intro.mp4"
    if os.path.exists(video_path):
        with open(video_path, "rb") as f:
            video_bytes = f.read()
        video_base64 = base64.b64encode(video_bytes).decode('utf-8')
        
        # Inject JavaScript to dynamically create the full-screen video background in the main DOM.
        # This completely avoids Streamlit markdown parser crashes and st.video default UI controls!
        js_code = f"""
        <script>
        const parentDoc = window.parent.document;
        if (!parentDoc.getElementById('custom-netflix-intro-overlay')) {{
            const overlay = parentDoc.createElement('div');
            overlay.id = 'custom-netflix-intro-overlay';
            Object.assign(overlay.style, {{
                position: 'fixed',
                top: '0',
                left: '0',
                width: '100vw',
                height: '100vh',
                backgroundColor: 'black',
                zIndex: '999999',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                opacity: '1',
                transition: 'opacity 0.8s ease-out',
                pointerEvents: 'none'
            }});
            
            const video = parentDoc.createElement('video');
            video.src = 'data:video/mp4;base64,{video_base64}';
            video.playsInline = true;
            video.controls = false; // No controls
            video.preload = 'auto'; // Immediate playback
            video.muted = false; // Attempt playing with original sound first!
            
            Object.assign(video.style, {{
                width: '100%',
                height: '100%',
                objectFit: 'cover', // Complete full-screen coverage
                filter: 'none',
                pointerEvents: 'none'
            }});
            
            // Try playing unmuted. If the browser's strict autoplay policy blocks the audio, 
            // we catch the error and instantly try again muted so the visual intro doesn't break!
            let playPromise = video.play();
            if (playPromise !== undefined) {{
                playPromise.catch(error => {{
                    video.muted = true;
                    video.play();
                }});
            }}
            
            // Fade out instantly after video completes
            video.onended = function() {{
                overlay.style.opacity = '0';
                setTimeout(() => {{ if (overlay.parentNode) overlay.parentNode.removeChild(overlay); }}, 800);
            }};
            
            // Fallback timeout
            setTimeout(() => {{
                if (overlay.parentNode) {{
                    overlay.style.opacity = '0';
                    setTimeout(() => {{ if (overlay.parentNode) overlay.parentNode.removeChild(overlay); }}, 800);
                }}
            }}, 5500);
            
            overlay.appendChild(video);
            parentDoc.body.appendChild(overlay);
        }}
        </script>
        """
        # Render the JS component without taking up any visual space in the Streamlit app
        components.html(js_code, height=0, width=0)
    else:
        st.markdown("""
        <style>
        .intro-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background-color: black;
            z-index: 999999;
            display: flex;
            justify-content: center;
            align-items: center;
            animation: fadeOutOverlay 0.8s ease-out forwards;
            animation-delay: 3.8s;
            pointer-events: none;
        }
        @keyframes fadeOutOverlay {
            0% { opacity: 1; visibility: visible; }
            100% { opacity: 0; visibility: hidden; }
        }
        </style>
        <div class="intro-overlay">
            <img src='https://media.tenor.com/RzKIoA1L2bUAAAAC/netflix-intro.gif' style='max-width: 100%; object-fit: contain;'>
        </div>
        """, unsafe_allow_html=True)

    st.session_state.intro_played = True

# --- Main Dashboard ---

st.markdown("""
<style>
/* Base Theme & Layout Reset */
.stApp {
    background-color: #141414 !important;
    background-image: radial-gradient(ellipse at top, rgba(229, 9, 20, 0.1) 0%, transparent 60%);
    color: #e5e5e5;
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    overflow-x: hidden;
}
#MainMenu, header, footer {visibility: hidden !important; display: none !important;}
.block-container {
    padding-top: 0 !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
    padding-bottom: 2rem !important;
    max-width: 100% !important;
}

/* Custom Header */
.netflix-navbar {
    position: fixed;
    top: 0; left: 0; width: 100%;
    height: 70px;
    background: linear-gradient(to bottom, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0) 100%);
    z-index: 1000;
    display: flex;
    align-items: center;
    padding: 0 4%;
    pointer-events: none;
}
.netflix-logo {
    color: #E50914;
    font-size: 2.2rem;
    font-weight: 900;
    letter-spacing: 1px;
}

/* Dynamic Hero Section */
.hero-container {
    position: relative;
    width: 100vw;
    height: 75vh;
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 0 4%;
    margin-bottom: -15vh; /* Pull inputs up over the gradient */
}
/* The dark vignette overlay */
.hero-vignette {
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    background: linear-gradient(to right, #141414 15%, transparent 60%),
                linear-gradient(to top, #141414 5%, transparent 40%);
    z-index: 1;
}
.hero-bottom-fade {
    position: absolute;
    bottom: 0; left: 0; width: 100%; height: 30vh;
    background: linear-gradient(to top, #141414 0%, transparent 100%);
    z-index: 2;
}

.hero-content {
    position: relative;
    z-index: 3;
    max-width: 50%;
    margin-top: 5vh;
}
.hero-title {
    font-size: 4.5rem;
    font-weight: 900;
    color: white;
    text-shadow: 2px 2px 8px rgba(0,0,0,0.8);
    line-height: 1.1;
    margin-bottom: 0.5rem;
}
.hero-meta {
    display: flex;
    gap: 15px;
    color: #a3a3a3;
    font-size: 1.1rem;
    font-weight: bold;
    margin-bottom: 1.5rem;
    align-items: center;
}
.match-score { color: #46d369; font-weight: 900; }
.hero-desc {
    font-size: 1.3rem;
    color: white;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.8);
    margin-bottom: 2rem;
    line-height: 1.4;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

/* Streamlit Input Reskinning (The Input Row) */
div[data-testid="stHorizontalBlock"] {
    position: relative;
    z-index: 10;
    padding: 0 4%;
}
div[data-testid="stSelectbox"] label, div[data-testid="stSlider"] label {
    display: none; /* Hide labels for absolute cleanliness */
}
div[data-testid="stSelectbox"] > div[data-baseweb="select"] {
    background-color: rgba(20,20,20,0.8) !important;
    border: 1px solid #333 !important;
    border-radius: 4px;
    color: white !important;
    backdrop-filter: blur(10px);
}
div[data-testid="stSelectbox"] > div[data-baseweb="select"]:focus-within {
    border-color: #E50914 !important;
}
div[data-testid="stSlider"] {
    padding: 10px 0;
}
div[data-baseweb="slider"] div[data-testid="stTickBar"] { display: none; }

/* Get Recommendations 'Play' Button */
div[data-testid="stButton"] > button {
    background-color: white !important;
    color: black !important;
    border: none;
    border-radius: 4px;
    padding: 0.6rem 2rem !important;
    font-size: 1.2rem !important;
    font-weight: 800;
    transition: all 0.2s;
    width: 100%;
}
div[data-testid="stButton"] > button:hover {
    background-color: rgba(255,255,255,0.7) !important;
}

/* Recommendation Carousel Container */
.carousel-section {
    position: relative;
    z-index: 5;
    padding: 0 4%;
    margin-top: 3rem;
}
.carousel-title {
    color: #e5e5e5;
    font-size: 1.6rem;
    font-weight: bold;
    margin-bottom: -15px; /* Pull rows closer */
}
.carousel-row {
    display: flex;
    flex-wrap: nowrap;
    overflow-x: auto;
    overflow-y: hidden;
    gap: 12px;
    padding: 30px 0 60px 0; /* Padding allows hover scale without clipping */
    scroll-behavior: smooth;
    -ms-overflow-style: none; /* IE and Edge */
    scrollbar-width: none; /* Firefox */
}
.carousel-row::-webkit-scrollbar { display: none; } /* Chrome */

/* Movie Cards */
.movie-card {
    flex: 0 0 auto;
    width: 260px;
    height: 146px; /* 16:9 aspect ratio */
    border-radius: 4px;
    background: #2b2b2b;
    position: relative;
    cursor: pointer;
    transition: transform 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94), z-index 0.4s;
    box-shadow: 0 4px 8px rgba(0,0,0,0.5);
    overflow: hidden;
}
.movie-card:hover {
    transform: scale(1.35) translateY(-5%);
    z-index: 100;
    border-radius: 6px;
    box-shadow: 0 10px 20px rgba(0,0,0,0.8);
}
.movie-title-overlay {
    position: absolute;
    bottom: 0; left: 0; width: 100%;
    padding: 15px 10px 10px 10px;
    background: linear-gradient(to top, rgba(0,0,0,0.9) 20%, transparent);
    color: white;
    font-weight: 800;
    font-size: 1.1rem;
    text-shadow: 1px 1px 2px black;
    z-index: 2;
    transition: opacity 0.3s;
}

/* Hover Content */
.movie-hover-info {
    position: absolute;
    bottom: 0; left: 0; width: 100%;
    background: linear-gradient(to top, #141414 100%, transparent);
    padding: 15px;
    opacity: 0;
    visibility: hidden;
    transition: opacity 0.3s;
    transition-delay: 0.2s;
    z-index: 3;
    display: flex;
    flex-direction: column;
    gap: 8px;
    height: 100%;
}
.movie-card:hover .movie-title-overlay { opacity: 0; transition-delay: 0s; }
.movie-card:hover .movie-hover-info { opacity: 1; visibility: visible; }

.card-actions {
    display: flex;
    gap: 10px;
}
.card-btn {
    width: 32px; height: 32px;
    border-radius: 50%;
    background-color: rgba(42,42,42,0.8);
    border: 2px solid rgba(255,255,255,0.5);
    color: white;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px;
    transition: all 0.2s;
    cursor: pointer;
}
.card-btn:hover { border-color: white; background-color: white; color: black; }
.card-btn.active { color: #E50914; border-color: #E50914; font-weight: bold; }

.card-meta { font-size: 0.8rem; color: #46d369; font-weight: bold; }
.card-tags { font-size: 0.75rem; color: #fff; display: flex; gap: 5px; flex-wrap: wrap; }
.tag { border: 1px solid rgba(255,255,255,0.4); border-radius: 3px; padding: 1px 6px; }
.why-tag { font-size: 0.7rem; color: #d2d2d2; margin-top: auto; padding-bottom: 2px; font-style: italic; }

/* Skeleton Loader Animation */
.skeleton-row {
    padding: 30px 0;
    display: flex; gap: 12px; overflow: hidden;
}
.skeleton-card {
    flex: 0 0 auto; width: 260px; height: 146px; border-radius: 4px;
    background: linear-gradient(90deg, #2b2b2b 0%, #3b3b3b 50%, #2b2b2b 100%);
    background-size: 400% 400%;
    animation: skeleton-pulse 1.5s ease-in-out infinite;
}
@keyframes skeleton-pulse { 0% {background-position: 0% 0%} 50% {background-position: -135% 0%} 100% {background-position: 0% 0%} }
</style>
""", unsafe_allow_html=True)

# Fixed Navbar
st.markdown("""
<div class="netflix-navbar">
    <div class="netflix-logo">NETFLIX</div>
</div>
""", unsafe_allow_html=True)

try:
    movies, item_similarity_df = load_and_prepare_data()
    
    available_movies = item_similarity_df.index.tolist()
    available_movies.sort()
    
    # State management for search input
    default_index = available_movies.index('Matrix, The (1999)') if 'Matrix, The (1999)' in available_movies else 0
    
    # Determine which movie to feature
    selected_movie = st.session_state.get("movie_select", available_movies[default_index])

    # Dynamic Hero Background based on selection
    import hashlib
    hash_val = int(hashlib.md5(selected_movie.encode()).hexdigest(), 16)
    bg_images = [
        "https://images.unsplash.com/photo-1536440136628-849c177e76a1?q=80&w=2025&auto=format&fit=crop", 
        "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?q=80&w=2070&auto=format&fit=crop", 
        "https://images.unsplash.com/photo-1440404653325-ab127d49abc1?q=80&w=2070&auto=format&fit=crop", 
        "https://images.unsplash.com/photo-1594909122845-11baa439b752?q=80&w=2070&auto=format&fit=crop"
    ]
    bg_img = bg_images[hash_val % len(bg_images)]
    match_score = 90 + (hash_val % 10)
    
    # Clean up title for hero
    clean_title = selected_movie.split(" (")[0]
    year_str = selected_movie.split("(")[-1].replace(")","") if "(" in selected_movie else "2024"
    
    hero_html = f"""
    <div class="hero-container" style="background-image: url('{bg_img}');">
        <div class="hero-vignette"></div>
        <div class="hero-bottom-fade"></div>
        <div class="hero-content">
            <div class="hero-title">{clean_title}</div>
            <div class="hero-meta">
                <span class="match-score">{match_score}% Match</span>
                <span>{year_str}</span>
                <span class="tag">HD</span>
                <span style="border: 1px solid gray; padding: 0 4px;">R</span>
            </div>
            <div class="hero-desc">
                An absolute masterpiece that redefines its genre. Discover the cinematic brilliance of '{clean_title}' and explore worlds like never before.
            </div>
        </div>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)
    
    # User Input Section
    col1, col2, col3, col4 = st.columns([3, 1.5, 2, 1])
    
    with col1:
        selected_movie = st.selectbox("Search Movie", available_movies, index=default_index, key="movie_select", label_visibility="collapsed")
    with col2:
        mood = st.selectbox("Mood", ["All Moods", "Dark & Gritty", "Feel-good", "Mind-bending", "Action-packed"], label_visibility="collapsed")
    with col3:
        num_recommendations = st.slider("Count", min_value=5, max_value=20, value=10, step=5, label_visibility="collapsed")
    with col4:
        get_rec = st.button("Generate ▶")

    if get_rec:
        st.markdown(f'<div class="carousel-section"><div class="carousel-title" id="results">Because you watched {clean_title}</div></div>', unsafe_allow_html=True)
        
        # Inject Javascript for the skeleton loader and actual loader transition
        skeleton_id = "skeleton-layer"
        skeleton_html = f"""
        <div id="{skeleton_id}" class="carousel-row" style="padding-left: 4%;">
            <div class="skeleton-card"></div><div class="skeleton-card"></div><div class="skeleton-card"></div><div class="skeleton-card"></div><div class="skeleton-card"></div>
        </div>
        """
        st.markdown(skeleton_html, unsafe_allow_html=True)
        
        # We don't really need a python time.sleep(), because the pure JS will handle revealing
        recommendations = get_recommendations(selected_movie, item_similarity_df, top_n=num_recommendations)
        
        if recommendations:
            cards_html = f'<div class="carousel-row" id="recommendation-carousel" style="display:none; padding-left: 4%;">'
            
            # List of high-quality cinematic Unsplash images for pseudo-posters
            poster_urls = [
                "https://images.unsplash.com/photo-1626814026160-2237a95fc5a0?q=80&w=500&auto=format&fit=crop", # Cyberpunk red/blue
                "https://images.unsplash.com/photo-1534447677768-be436bb09401?q=80&w=500&auto=format&fit=crop", # Fantasy/SciFi
                "https://images.unsplash.com/photo-1505691938895-1758d7feb511?q=80&w=500&auto=format&fit=crop", # Dark thriller
                "https://images.unsplash.com/photo-1478720568477-152d9b164e26?q=80&w=500&auto=format&fit=crop", # Drama/Cinema
                "https://images.unsplash.com/photo-1618331835717-801e976710b2?q=80&w=500&auto=format&fit=crop", # Action/Colorful
                "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?q=80&w=500&auto=format&fit=crop", # Romance
                "https://images.unsplash.com/photo-1533130061792-64b345e4a833?q=80&w=500&auto=format&fit=crop", # Cyberpunk street
                "https://images.unsplash.com/photo-1485846234645-a62644f84728?q=80&w=500&auto=format&fit=crop", # Vintage reel
                "https://images.unsplash.com/photo-1552820728-8b83bb6b773f?q=80&w=500&auto=format&fit=crop", # Horror dark
                "https://images.unsplash.com/photo-1514315384763-ba401779410f?q=80&w=500&auto=format&fit=crop", # History
                "https://images.unsplash.com/photo-1574267432553-4b4628081524?q=80&w=500&auto=format&fit=crop", # Neon sign
                "https://images.unsplash.com/photo-1500462918059-b1a0cb512f1d?q=80&w=500&auto=format&fit=crop"  # Beautiful gradient neon
            ]
            
            for movie in recommendations:
                m_hash = int(hashlib.md5(movie.encode()).hexdigest(), 16)
                m_score = 80 + (m_hash % 19)
                
                # Fetch a random pseudo-poster based on the title hash
                bg_image_url = poster_urls[m_hash % len(poster_urls)]
                
                # Subtle dark gradient fading up from bottom + the cinematic image underneath
                bg_style = f"linear-gradient(to top, rgba(0,0,0,1) 0%, rgba(0,0,0,0) 80%), url('{bg_image_url}') center/cover no-repeat"
                
                m_clean_title = movie.split(" (")[0]
                safe_title = m_clean_title.replace('"', '&quot;')
                safe_movie = movie.replace('"', '&quot;')
                
                cards_html += f"""<div class="movie-card" style="background: {bg_style};">
                    <div class="movie-title-overlay">{m_clean_title}</div>
                    <div class="movie-hover-info">
                        <div class="card-actions">
                            <button class="card-btn" onclick="pDoc.togglePlay(this)">▶</button>
                            <button class="card-btn add-btn" data-movie="{safe_movie}" onclick="pDoc.togglePick(this)">+</button>
                            <button class="card-btn like-btn" data-movie="{safe_movie}" onclick="pDoc.toggleLike(this)">♥</button>
                        </div>
                        <div class="card-meta"><span style="color:#d2d2d2;">{m_clean_title}</span></div>
                        <div class="card-tags">
                            <span class="tag">{['Action','Drama','Sci-Fi','Comedy','Thriller'][m_hash%5]}</span>
                        </div>
                        <div class="why-tag">Recommended for you</div>
                    </div>
                </div>"""
            cards_html += '</div>'
            
            # Place an empty container for the cards to bypass Streamlit Markdown bugs
            st.markdown('<div id="recommendations-container"></div>', unsafe_allow_html=True)
            cards_html_escaped = cards_html.replace('`', '\\`').replace('$', '\\$')
            
            # Use components.html to inject logic that explicitly sets innerHTML and safely handles state
            js_script = f"""
            <script>
            const pDoc = window.parent.document;
            
            pDoc.togglePlay = function(btn) {{
                btn.style.backgroundColor = 'white';
                btn.style.color = 'black';
            }};
            
            pDoc.toggleLike = function(btn) {{
                const movieTitle = btn.getAttribute('data-movie');
                btn.classList.toggle('active');
                let likes = JSON.parse(localStorage.getItem('netflix-likes') || '{{}}');
                likes[movieTitle] = btn.classList.contains('active');
                localStorage.setItem('netflix-likes', JSON.stringify(likes));
            }};
            
            pDoc.togglePick = function(btn) {{
                const movieTitle = btn.getAttribute('data-movie');
                let picks = JSON.parse(localStorage.getItem('netflix-picks') || '{{}}');
                // Use innerHTML instead of innerText per requirements
                if (btn.innerHTML.includes('+')) {{
                    btn.innerHTML = '✓';
                    btn.classList.add('active');
                    picks[movieTitle] = true;
                }} else {{
                    btn.innerHTML = '+';
                    btn.classList.remove('active');
                    delete picks[movieTitle];
                }}
                localStorage.setItem('netflix-picks', JSON.stringify(picks));
            }};
            
            // Execute the skeleton reveal and state syncing
            setTimeout(() => {{
                // Inject the cards safely via innerHTML to DOM to avoid any Markdown text rendering bugs
                const container = pDoc.getElementById('recommendations-container');
                if (container) {{
                    container.innerHTML = `{cards_html_escaped}`;
                }}
            
                const skeleton = pDoc.getElementById('{skeleton_id}');
                const carousel = pDoc.getElementById('recommendation-carousel');
                
                if (skeleton && carousel) {{
                    skeleton.style.display = 'none';
                    carousel.style.display = 'flex';
                    
                    // Smooth scroll to the results title
                    const title = pDoc.getElementById('results');
                    if (title) title.scrollIntoView({{behavior: 'smooth', block: 'center'}});
                    
                    // Apply saved local storage states to the buttons
                    const likes = JSON.parse(localStorage.getItem('netflix-likes') || '{{}}');
                    const picks = JSON.parse(localStorage.getItem('netflix-picks') || '{{}}');
                    
                    const likeBtns = carousel.querySelectorAll('.like-btn');
                    likeBtns.forEach(btn => {{
                        const movie = btn.getAttribute('data-movie');
                        if (movie && likes[movie]) btn.classList.add('active');
                    }});
                    
                    const addBtns = carousel.querySelectorAll('.add-btn');
                    addBtns.forEach(btn => {{
                        const movie = btn.getAttribute('data-movie');
                        if (movie && picks[movie]) {{
                            btn.innerHTML = '✓';
                            btn.classList.add('active');
                        }}
                    }});
                }}
            }}, 800); // 800ms of skeleton loading

            </script>
            """
            import streamlit.components.v1 as components
            components.html(js_script, height=0, width=0)
            
        else:
            st.warning("Sorry, we couldn't find enough data to recommend similar movies.")

except Exception as e:
    st.error(f"An error occurred: {e}")

