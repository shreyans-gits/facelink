# FACELINK
> Real-time face recognition for the people you know. Enroll once, recognized forever.

![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![OpenCV](https://img.shields.io/badge/opencv-4.x-green) ![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## What it does

FaceLink watches your webcam and greets whoever it sees — by name. You enroll people once (manually, from Google Photos, or automatically from a photo dump using face clustering), and the system remembers them using face embeddings and cosine similarity matching. No cloud, no training, everything runs locally.

---

## How it works

1. A pretrained model converts each face into a 128-number vector called an **embedding**
2. Embeddings for known people are stored locally in a `.pkl` database
3. On each webcam frame, new faces are embedded and compared against stored ones using **cosine similarity**
4. If the similarity clears a threshold, the person is identified — otherwise they're marked Unknown

---

## Project structure

```
facelink/
├── config.py              # Constants — threshold, paths, embedding size
├── detector.py            # Face detection on images and video frames
├── embedder.py            # 128-dim embedding extraction via pretrained model
├── enrollment.py          # Multi-sample enrollment + local pickle database
├── matcher.py             # Cosine similarity matching with threshold
├── main.py                # Real-time webcam recognition loop
├── enroll.py              # Manual enrollment from local photos
├── cluster_enroll.py      # Automatic enrollment via DBSCAN face clustering
├── google_photos.py       # Google OAuth + Picker API + photo download
├── google_enroll.py       # End-to-end Google Photos enrollment flow
├── data/
│   └── enrolled/
└── photos/                # Drop manual enrollment photos here
```

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/facelink.git
cd facelink
```

### 2. Create a virtual environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
```

### 3. Install dependencies

```bash
pip install opencv-python face-recognition numpy scikit-learn google-auth-oauthlib google-auth-httplib2 google-api-python-client requests
```

### 4. Python 3.13 compatibility fix

`face_recognition` uses a legacy package discovery method that breaks on Python 3.13. `main.py`, `enroll.py`, `google_enroll.py`, and `cluster_enroll.py` each include a spoof block at the top that manually injects the model file paths. Update the `venv_site` path in each file to match your local environment:

```python
venv_site = r"path\to\your\venv\Lib\site-packages"
```

---

## Enrolling people

### Option A — Manual (local photos)

Drop photos into the `photos/` folder and edit `enroll.py` with the name and paths, then run:

```bash
python enroll.py
```

Multiple photos per person improve accuracy — use varied lighting and angles.

### Option B — Google Photos Picker

**One-time setup:**

1. Go to [Google Cloud Console](https://console.cloud.google.com) and enable the **Google Photos Picker API**
2. Create an OAuth 2.0 Desktop App credential and download it as `credentials.json` into the project root
3. Add the scope `https://www.googleapis.com/auth/photospicker.mediaitems.readonly`

**Enroll from Google Photos:**

```bash
python google_enroll.py
```

This opens a browser, lets you pick photos directly from your Google Photos library, downloads them locally, and enrolls the person automatically. You'll be asked for the person's name after selection.

> Note: Google Photos' People/face-tagging feature is not exposed via their API, so photo selection is manual through the Picker UI.

### Option C — Cluster enrollment from a photo dump (recommended)

The most powerful enrollment method. Point it at any folder of photos — a Google Takeout export, a camera roll dump, anything — and it automatically groups faces by identity using DBSCAN clustering. You label each cluster once, and everyone gets enrolled in one pass.

```bash
python cluster_enroll.py
```

Edit the `takeout_path` variable at the bottom of `cluster_enroll.py` to point at your photo folder before running.

**How it works:**
1. Scans every image in the folder and extracts face embeddings
2. Runs DBSCAN (cosine metric, `eps=0.05`) to group similar faces into clusters
3. Shows you a cropped face from each cluster and asks for the person's name
4. Enrolls all faces in that cluster under that name
5. Faces that don't cluster with anyone (strangers, blurry shots) are automatically ignored as noise

---

## Running

```bash
python main.py
```

Press `q` to quit.

---

## Performance notes

- Detection runs on frames downscaled to 25% and scaled back up — reduces pixel load by ~9x
- Recognition runs every 5th frame, with the last result reused in between
- Bounding boxes and names persist smoothly across skipped frames

---

## Tuning

Adjust `SIMILARITY_THRESHOLD` in `config.py`:

- **Higher (e.g. 0.7)** — stricter matching, fewer false positives, more Unknowns
- **Lower (e.g. 0.5)** — more lenient, recognizes from farther or at worse angles

Adjust `eps` in `cluster_enroll.py` if clustering results are off:

- **Lower (e.g. 0.03)** — tighter clusters, splits one person into multiple groups if photos vary a lot
- **Higher (e.g. 0.1)** — looser clusters, may merge different people if they look similar

---

## What's not included

- `credentials.json` — your Google OAuth credentials (never commit this)
- `token.json` — generated after first Google login (never commit this)
- `enrolled_faces.pkl` — your local face database (personal data)

All three are in `.gitignore`.

---

## Concepts covered

- Face embeddings and vector representations of identity
- Cosine similarity for comparing high-dimensional vectors
- Transfer learning — using a pretrained model as a feature extractor
- Unsupervised clustering with DBSCAN for automatic identity grouping
- Real-time video processing with OpenCV
- OAuth 2.0 authentication flow
- Google Photos Picker API integration
- Local data persistence with pickle
