# Installation

## Prerequisites

- Python 3.11 or higher
- Windows 10/11 (for desktop app)
- ~200MB free disk space (for Whisper model, optional)

## Install Dependencies

```bash
git clone https://github.com/englishcoachpro/EnglishCoachPro.git
cd EnglishCoachPro
pip install -r requirements.txt
```

## Run the App

```bash
python main.py
```

## Build the EXE

```bash
pyinstaller --onefile --windowed \
            --add-data "data/seed;data/seed" \
            --hidden-import=customtkinter \
            --hidden-import=sqlalchemy \
            --name "EnglishCoachPro" \
            main.py
```

The built EXE will be in `dist/EnglishCoachPro.exe`.

## Optional: Whisper Model for Pronunciation

The pronunciation coach uses openai-whisper. On first use, it will prompt
you to download the "tiny" model (~75MB). You can skip this if you don't
need pronunciation features.
