# WikiTrust Index

A comprehensive Wikipedia article analysis tool that provides trust scores, AI content risk assessment, and detailed article metrics for Swahili Wikipedia articles.

## 🌟 Features

### Article Analysis & Trust Scoring
- **Trust Score**: 0-100% rating based on article quality indicators
- **AI Content Risk**: Detects potential AI-generated content patterns
- **Content Type**: Identifies article type (standard, disambiguation, redirect)

### Comprehensive Article Metrics
- **Links Analysis**: Counts internal and external links
- **Broken Links**: Identifies and counts broken external references
- **Categories**: Full list of Wikipedia categories with smart parsing
- **Birth/Death Information**: Extracts birth and death years from categories
- **Living Status**: Detects if subject is living or deceased
- **Stub Detection**: Identifies incomplete articles

### AI-Powered Insights
- **AI Analysis**: Detailed explanation of findings and patterns
- **Smart Recommendations**: Actionable suggestions for article improvement
- **Content Quality Assessment**: Heuristic-based quality scoring

### User Interface
- **Modern Design**: Clean, responsive Bootstrap-based interface
- **Real-time Analysis**: Instant results from Wikipedia API
- **Demo Mode**: Test with sample data when backend is unavailable
- **Loading States**: Visual feedback during analysis

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ and npm
- Python 3.8+ and pip

### Frontend Setup
```bash
cd app
npm install
npm run dev
```

### Backend Setup
```bash
cd server
pip install -r requirements.txt
python main.py
```

### Usage
1. Open the frontend in your browser (usually http://localhost:5173)
2. Enter a Wikipedia article title in Swahili
3. Click "Analyze" to get comprehensive analysis
4. Use "Load Demo Data" to test without backend

## 🔧 How It Works

### Frontend (Vue.js)
- **SearchBar**: Article title input and search
- **ArticleCard**: Displays article summary and trust score
- **AnalysisPanel**: Shows detailed metrics and analysis
- **LinksList**: Displays internal and external links
- **Recommendations**: Provides improvement suggestions

### Backend (FastAPI)
- **Wikipedia API Integration**: Fetches article data and metadata
- **MediaWiki Action API**: Extracts links, categories, and references
- **AI Risk Detection**: Pattern-based AI content identification
- **Link Validation**: Checks external link accessibility
- **Smart Parsing**: Extracts birth/death years from categories

### Data Flow
1. User enters article title
2. Frontend calls Wikipedia REST API for summary
3. Backend analyzes article with MediaWiki Action API
4. AI risk assessment and pattern detection
5. Link validation and category parsing
6. Comprehensive analysis results returned
7. Frontend displays formatted results

## 📊 Sample Analysis Results

For the article "Costantino Castriota":

- **Trust Score**: 2%
- **AI Content Risk**: 2% (Low)
- **Content Type**: Article
- **Categories**: 9 categories including birth/death years
- **Birth Year**: 1477
- **Death Year**: 1500
- **Status**: Deceased
- **Stub**: Yes (incomplete article)
- **Internal Links**: 12
- **External Links**: 3

## 🎯 Use Cases

- **Wikipedia Editors**: Identify articles needing improvement
- **Researchers**: Assess article quality and completeness
- **Content Moderators**: Detect AI-generated content
- **Students**: Evaluate source reliability
- **Librarians**: Quality assessment for reference materials

## 🔍 Technical Details

### API Endpoints
- `POST /analyze`: Main analysis endpoint
- Input: `{"title": "article_title"}`
- Output: Comprehensive analysis object

### Data Models
- **AnalyzeRequest**: Input validation
- **AnalyzeResponse**: Structured analysis results
- **Sample Data**: Fallback data for testing

### Error Handling
- Graceful fallback when backend unavailable
- Sample data loading for demonstration
- Comprehensive error logging

## 🛠️ Development

### Project Structure
```
WikiTrust Index/
├── app/                 # Vue.js frontend
│   ├── src/
│   │   ├── components/ # Vue components
│   │   ├── sampleData.js
│   │   └── App.vue
│   └── package.json
├── server/              # FastAPI backend
│   ├── main.py
│   └── requirements.txt
└── README.md
```

### Key Components
- **AnalysisPanel**: Main metrics display
- **LinksList**: Link management and display
- **Recommendations**: AI-powered suggestions
- **SearchBar**: Article search interface

### Testing
- Use "Load Demo Data" button for frontend testing
- Backend can be tested independently
- Sample data provides realistic test scenarios

## 🌐 Supported Languages

Currently optimized for **Swahili Wikipedia** with:
- Swahili category parsing
- Localized recommendations
- Swahili Wikipedia API integration

## 📈 Future Enhancements

- Multi-language support
- Advanced AI content detection
- Historical analysis tracking
- User authentication and saved analyses
- API rate limiting and caching
- Mobile app development

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

For issues and questions:
- Check the demo mode for interface testing
- Review the sample data for expected results
- Ensure both frontend and backend are running
- Check browser console for error messages

---

**WikiTrust Index** - Making Wikipedia articles more trustworthy, one analysis at a time.
