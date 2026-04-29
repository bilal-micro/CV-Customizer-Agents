# ATS Agentic System

An intelligent CV optimization platform that uses AI agents to analyze, enhance, and iteratively improve resumes for maximum ATS (Applicant Tracking System) compatibility and recruiter appeal.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![React](https://img.shields.io/badge/React-18+-61DAFB.svg)
![Django](https://img.shields.io/badge/Django-4.2+-092E20.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 🚀 Features

- **Intelligent Keyword Extraction**: Automatically extracts and prioritizes keywords from job descriptions
- **CV-Job Matching**: Analyzes your CV against job requirements with detailed feedback
- **ATS Scoring**: Rates your CV against ATS parsing and ranking standards
- **Iterative Optimization**: Up to 3 iterations of AI-powered CV improvement
- **Multi-Agent Architecture**: Specialized AI agents for different analysis tasks
- **Real-time Progress Tracking**: Visual tracking of optimization process
- **Flexible LLM Integration**: Works with Ollama and external LLM services

## 🛠️ Tech Stack

### Backend
- **Python 3.8+**: Core language
- **Django 4.2+**: Web framework
- **Django REST Framework**: API layer
- **SQLite**: Default database (configurable)
- **Ollama**: Local LLM with llama3.1 model

### Frontend
- **React 19**: UI framework
- **TypeScript**: Type safety
- **Vite**: Build tool and dev server
- **Axios**: HTTP client
- **React Router**: Client-side routing

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.8 or higher
- Node.js 16 or higher
- Ollama (with llama3.1 model installed)
- Git

## 🚦 Quick Start

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd ATS-Agentic
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser (optional, for admin panel)
python manage.py createsuperuser

# Start Django development server
python manage.py runserver
```

The backend will be available at `http://localhost:8000`

### 3. Frontend Setup

```bash
# Open a new terminal and navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

### 4. Start Ollama

```bash
# In a third terminal
ollama run llama3.1
```

## 📁 Project Structure

```
ATS-Agentic/
├── backend/                 # Django backend application
│   ├── ats_app/            # Main Django app
│   │   ├── agents/         # AI agent implementations
│   │   │   ├── keyword_extractor.py
│   │   │   ├── keyword_matcher.py
│   │   │   ├── cv_matcher.py
│   │   │   ├── cv_updater.py
│   │   │   ├── ats_rater.py
│   │   │   ├── match_evaluator.py
│   │   │   └── orchestrator.py
│   │   ├── models.py       # Database models
│   │   ├── serializers.py  # DRF serializers
│   │   ├── views.py        # API endpoints
│   │   └── services/       # Utility services
│   ├── ats_project/        # Django project settings
│   └── manage.py
│
├── frontend/                # React frontend application
│   ├── src/
│   │   ├── api/           # API client
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   └── types/         # TypeScript types
│   ├── package.json
│   └── vite.config.ts
│
├── docs/                   # Comprehensive documentation
│   ├── README.md          # Main documentation index
│   ├── ARCHITECTURE.md    # System architecture
│   ├── WORKFLOW.md        # Workflow documentation
│   ├── API.md             # API reference
│   ├── AGENTS.md          # Agent documentation
│   ├── DATA_MODELS.md     # Data models
│   ├── USER_GUIDE.md      # User guide
│   ├── DEVELOPER_GUIDE.md # Developer guide
│   └── diagrams/          # Architecture diagrams
│
└── README.md              # This file
```

## 🔄 How It Works

### Two-Phase Process

#### Phase 1: Initial Analysis (One-time)
1. Extract prioritized keywords from job requirements
2. Match your CV against those keywords
3. Calculate initial match rate and ATS score

#### Phase 2: Iterative Optimization (Max 3 iterations)
For each iteration:
1. Generate an optimization prompt for an external LLM
2. Use the prompt with your preferred LLM service
3. Submit the updated CV back to the system
4. Re-match and re-rate the CV
5. Evaluate results and continue or finish

### Agent Pipeline

```
KeywordExtractor → CVMatcher → CVUpdater → ATSRater
                      ↓
              EnhancedKeywordMatcher
              SectionAnalyzer
              MatchEvaluator
              AnalysisSynthesizer
```

## 📚 Documentation

For detailed information, please refer to the documentation in the `/docs` directory:

- [Getting Started Guide](docs/README.md)
- [System Architecture](docs/ARCHITECTURE.md)
- [Workflow Documentation](docs/WORKFLOW.md)
- [API Reference](docs/API.md)
- [Agent Documentation](docs/AGENTS.md)
- [Data Models](docs/DATA_MODELS.md)
- [User Guide](docs/USER_GUIDE.md)
- [Developer Guide](docs/DEVELOPER_GUIDE.md)

## ⚙️ Configuration

### Backend Configuration

Edit `backend/ats_project/settings.py` to configure:

- Database settings
- CORS settings
- Debug mode
- Allowed hosts
- Ollama endpoint

### Frontend Configuration

Edit `frontend/src/api/index.ts` to configure:

- API base URL
- Request/response interceptors

### Environment Variables

Create a `.env` file in the backend directory:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
OLLAMA_HOST=http://localhost:11434
```

## 🧪 Testing

### Backend Tests

```bash
cd backend
python manage.py test
```

### Frontend Tests

```bash
cd frontend
npm test
```

## 🐛 Troubleshooting

### Common Issues

**Process stuck in "running" state**
- Check backend logs for errors
- Ensure Ollama is running with llama3.1 model
- Verify database connection

**Low match rate**
- Ensure job description is detailed
- Check CV formatting and structure
- Verify LaTeX CV is properly formatted

**External LLM generates invalid LaTeX**
- Validate LaTeX before submitting
- Use high-quality LLM services
- Check for syntax errors

## 📊 Success Criteria

The system considers a CV optimized when:
- **ATS Score ≥ 80%**: Meets ATS parsing and ranking standards
- **Match Rate ≥ 75%**: Sufficient keyword coverage and alignment
- **Recruiter Appeal ≥ 75%**: Strong human-readable appeal

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Belal Hassan** - [belal-hassan.com](https://belal-hassan.com)

## 🙏 Acknowledgments

- Built with [Django](https://www.djangoproject.com/)
- Frontend powered by [React](https://reactjs.org/)
- AI integration using [Ollama](https://ollama.com/)
- Icons and visual assets from various open sources

---

**Version**: 1.0.0  
**Last Updated**: April 19, 2026