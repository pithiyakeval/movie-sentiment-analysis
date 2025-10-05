import nltk
import os

def download_nltk_data():
    data_dir = '/usr/local/nltk_data'
    
    print("Creating NLTK data directory...")
    os.makedirs(data_dir, exist_ok=True)
    
    # Add to nltk path
    nltk.data.path.append(data_dir)
    
    print("Downloading NLTK datasets...")
    
    packages = ['vader_lexicon', 'punkt', 'stopwords', 'averaged_perceptron_tagger']
    
    for package in packages:
        try:
            print(f"Downloading {package}...")
            nltk.download(package, download_dir=data_dir)
            print(f"✓ {package} downloaded")
        except Exception as e:
            print(f"✗ Failed to download {package}: {e}")
    
    print("NLTK download process completed!")
    
    # Simple file existence check
    vader_path = os.path.join(data_dir, 'sentiment', 'vader_lexicon.zip')
    if os.path.exists(vader_path):
        print(f"✓ VADER lexicon exists at: {vader_path}")
    else:
        print(f"✗ VADER lexicon not found at: {vader_path}")
    
    return True

if __name__ == "__main__":
    download_nltk_data()