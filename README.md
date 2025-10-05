🛠️ Technology Stack
Backend: Python, Flask

NLP: NLTK with VADER Sentiment Analyzer

Database: PostgreSQL

Containerization: Docker, Docker Compose

CI/CD: GitHub Actions

Testing: Pytest

🏗️ Project Structure
text
movie-sentiment-analysis/
├── flask-app/
│   ├── app.py              # Main Flask application
│   ├── model.py            # Sentiment analysis logic
│   ├── utils.py            # Utility functions
│   ├── requirements.txt    # Python dependencies
│   └── test_app.py         # Unit tests
├── .github/workflows/
│   └── ci-cd.yml          # CI/CD pipeline
├── docker-compose.yml     # Docker Compose configuration
├── Dockerfile            # Docker image definition
├── deploy.sh            # Deployment script
└── README.md            # Project documentation
🔧 Development
Local Development Setup
Create virtual environment

bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies

bash
pip install -r flask-app/requirements.txt
Run the application

bash
cd flask-app
python app.py
Running Tests
bash
# Run unit tests
python -m pytest flask-app/test_app.py -v

# Run with coverage
python -m pytest flask-app/test_app.py --cov=flask-app --cov-report=html
📊 Sentiment Analysis
The API uses VADER (Valence Aware Dictionary and sEntiment Reasoner) which is specifically attuned to sentiments expressed in social media and works well on short texts like movie reviews.

Sentiment Categories:

Positive: compound score >= 0.05

Neutral: compound score between -0.05 and 0.05

Negative: compound score <= -0.05

🐳 Docker Commands
Build and Run
bash
# Build image
docker build -t movie-sentiment-api .

# Run container
docker run -p 5000:5000 movie-sentiment-api
Database Operations
bash
# Access PostgreSQL database
docker exec -it postgres-db psql -U postgres -d moviesentiment

# View logs
docker-compose logs -f
Cleanup
bash
# Stop and remove containers
docker-compose down

# Remove all containers, networks, and volumes
docker-compose down -v
🔄 CI/CD Pipeline
The project includes GitHub Actions workflow that automatically:

Runs tests on every push and pull request

Builds Docker images

Deploys to production (configurable)

View workflow runs in the Actions tab of your GitHub repository.

🤝 Contributing
Fork the repository

Create a feature branch (git checkout -b feature/amazing-feature)

Commit your changes (git commit -m 'Add amazing feature')

Push to the branch (git push origin feature/amazing-feature)

Open a Pull Request

📝 License
This project is licensed under the MIT License - see the LICENSE file for details.

👨‍💻 Author
Keval Pithiya

GitHub: @pithiyakeval

Email: kevala053@gmail.com

🙏 Acknowledgments
NLTK team for the VADER sentiment analysis tool

Flask community for excellent documentation

Docker for containerization platform

