import os
import streamlit as st
from dotenv import load_dotenv
from anthropic import Anthropic
import re
from urllib.parse import quote

load_dotenv()

client = Anthropic(
    base_url=os.getenv("ANTRHOPIC_BASE_URL"),
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

def ask_ai(prompt):
    res = client.messages.create(
        model="claude-haiku", max_tokens=1024, messages=[{"role": "user", "content": prompt}]
    )
    return res.content[0].text

def set_page_style():
    st.set_page_config(
        page_title="🎵 Music DJ - AI 추천",
        page_icon="🎵",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    st.markdown("""
    <style>
        * {
            margin: 0;
            padding: 0;
        }

        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        .stApp {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        }

        .main {
            padding: 2rem;
        }

        h1 {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            margin-bottom: 1rem;
            font-size: 3rem !important;
            text-align: center;
        }

        .subtitle {
            text-align: center;
            color: #a0aec0;
            margin-bottom: 2rem;
            font-size: 1.1rem;
        }

        .input-container {
            background: rgba(255, 255, 255, 0.05);
            border: 2px solid rgba(102, 126, 234, 0.3);
            border-radius: 15px;
            padding: 2rem;
            margin-bottom: 2rem;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }

        .stSelectbox, .stTextInput, .stSlider {
            margin-bottom: 1rem;
        }

        .stSelectbox > label, .stTextInput > label, .stSlider > label {
            color: #e2e8f0 !important;
            font-weight: 600;
            font-size: 1rem;
        }

        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 12px 32px;
            font-size: 1.1rem;
            font-weight: 600;
            width: 100%;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }

        .stButton > button:active {
            transform: translateY(0);
        }

        .music-card {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
            border: 2px solid rgba(102, 126, 234, 0.5);
            border-radius: 15px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
        }

        .music-card:hover {
            border-color: rgba(102, 126, 234, 0.8);
            box-shadow: 0 12px 40px rgba(102, 126, 234, 0.4);
            transform: translateY(-5px);
        }

        .song-number {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 1.2rem;
            margin-bottom: 0.5rem;
        }

        .song-title {
            color: #fff;
            font-size: 1.3rem;
            font-weight: 700;
            margin: 0.5rem 0;
        }

        .song-artist {
            color: #cbd5e0;
            font-size: 1rem;
            margin-bottom: 0.5rem;
        }

        .song-genre {
            color: #a0aec0;
            font-size: 0.9rem;
            margin-bottom: 1rem;
        }

        .button-container {
            display: flex;
            gap: 1rem;
            margin-top: 1rem;
        }

        .youtube-btn {
            background: linear-gradient(135deg, #ff0000 0%, #cc0000 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            box-shadow: 0 4px 12px rgba(255, 0, 0, 0.3);
        }

        .youtube-btn:hover {
            background: linear-gradient(135deg, #ff3333 0%, #dd0000 100%);
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(255, 0, 0, 0.5);
        }

        .results-container {
            margin-top: 2rem;
        }

        .results-title {
            color: #e2e8f0;
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            text-align: center;
        }

        .loading-spinner {
            text-align: center;
            color: #667eea;
            font-size: 1.2rem;
        }
    </style>
    """, unsafe_allow_html=True)

def parse_songs(text):
    songs = []

    lines = text.strip().split('\n')
    current_song = {}

    for line in lines:
        line = line.strip()
        if not line:
            if current_song and 'title' in current_song:
                songs.append(current_song)
                current_song = {}
            continue

        if any(line.startswith(prefix) for prefix in ['곡:', '제목:', 'Song:', 'Title:', '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.']):
            if current_song and 'title' in current_song:
                songs.append(current_song)
            current_song = {'title': line.split(':', 1)[-1].strip() if ':' in line else line, 'artist': '', 'genre': ''}

        elif any(line.lower().startswith(prefix) for prefix in ['가수:', '아티스트:', 'artist:', 'singer:']):
            current_song['artist'] = line.split(':', 1)[-1].strip()

        elif any(line.lower().startswith(prefix) for prefix in ['장르:', 'genre:']):
            current_song['genre'] = line.split(':', 1)[-1].strip()

    if current_song and 'title' in current_song:
        songs.append(current_song)

    if not songs:
        pattern = r'([^()\n]+)\s*\(\s*([^)]+)\s*\)|([^-\n]+)\s*-\s*([^\n]+)'
        matches = re.findall(pattern, text)
        for match in matches:
            if match[0] and match[1]:
                songs.append({'title': match[0].strip(), 'artist': match[1].strip(), 'genre': ''})
            elif match[2] and match[3]:
                songs.append({'title': match[2].strip(), 'artist': match[3].strip(), 'genre': ''})

    return songs

def main():
    set_page_style()

    st.markdown("<h1>🎵 Music DJ</h1>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>AI 기반 음악 추천 서비스</div>", unsafe_allow_html=True)

    with st.container():
        st.markdown("<div class='input-container'>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            situation = st.selectbox(
                "🎭 상황을 선택해주세요",
                ["공부", "운동", "휴식", "파티", "드라이브", "작업", "명상", "커피숍"]
            )

        with col2:
            artist = st.text_input(
                "🎤 좋아하는 가수",
                placeholder="예: 아이유, The Weeknd"
            )

        col3, col4 = st.columns(2)
        with col3:
            genre = st.text_input(
                "🎸 선호 장르",
                placeholder="예: K-pop, 록, 재즈"
            )

        with col4:
            num_songs = st.slider(
                "📊 추천 곡 수",
                min_value=1,
                max_value=10,
                value=5
            )

        st.markdown("</div>", unsafe_allow_html=True)

    if st.button("🎶 추천곡 생성하기", use_container_width=True):
        with st.spinner("🎵 DJ가 곡을 선택 중입니다..."):
            prompt = f"""당신은 뛰어난 음악 DJ입니다.
사용자의 취향과 상황에 맞는 음악을 추천해주세요.

상황: {situation}
좋아하는 가수: {artist if artist else '특정 가수 없음'}
선호 장르: {genre if genre else '특정 장르 없음'}
추천 곡 수: {num_songs}

다음 형식으로 {num_songs}개의 곡을 추천해주세요:
곡: [곡 제목]
가수: [가수명]
장르: [장르]

---
[다음 곡으로]"""

            result = ask_ai(prompt)

            st.markdown("<div class='results-container'>", unsafe_allow_html=True)
            st.markdown("<div class='results-title'>✨ AI DJ의 추천곡</div>", unsafe_allow_html=True)

            songs = parse_songs(result)

            if not songs:
                lines = result.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        songs.append({
                            'title': line.strip(),
                            'artist': '',
                            'genre': ''
                        })

            for idx, song in enumerate(songs[:num_songs], 1):
                with st.container():
                    st.markdown(f"""
                    <div class='music-card'>
                        <div class='song-number'>{idx}</div>
                        <div class='song-title'>🎵 {song.get('title', 'Unknown')}</div>
                        <div class='song-artist'>👤 {song.get('artist', 'Unknown Artist')}</div>
                        <div class='song-genre'>🎸 {song.get('genre', 'Genre')}</div>
                    """, unsafe_allow_html=True)

                    youtube_query = f"{song.get('title', '')} {song.get('artist', '')}"
                    youtube_url = f"https://www.youtube.com/results?search_query={quote(youtube_query)}"

                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"""
                        <a href="{youtube_url}" target="_blank" class='youtube-btn'>
                            ▶ 유튜브에서 듣기
                        </a>
                        """, unsafe_allow_html=True)

                    st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()