# VectorTutor

A comprehensive AI-powered study assistant built with Streamlit and Groq API. This application uses 5 specialized agents to help you learn effectively from PDF documents.

## 🎯 Features

### 5 Specialized AI Agents

1. **📄 Reader Agent**: Extracts and structures content from PDF documents
2. **🎴 Flashcard Agent**: Generates Q&A flashcards for active recall practice
3. **📝 Quiz Agent**: Creates adaptive multiple-choice questions (easy/medium/hard)
4. **📅 Planner Agent**: Builds personalized revision schedules
5. **💬 Chat Agent**: Answers questions and summarizes notes from PDF context

### Key Capabilities

- **PDF Processing**: Upload and extract text from PDF documents
- **Flashcard Generation**: Create study flashcards with questions and answers
- **Adaptive Quizzes**: Generate quizzes with different difficulty levels
- **Revision Planning**: Create personalized study schedules
- **Q&A Chat**: Ask questions about your documents and get AI-powered answers
- **Performance Tracking**: Monitor your quiz performance and accuracy
- **Note Summarization**: Generate concise summaries of your notes

## 🏗️ Architecture

```
Knowledge Memory (SQLite) ← All agents read/write here
    ↓
1. Reader Agent: Extract & structure PDF content
2. Flashcard Agent: Generate Q&A flashcards  
3. Quiz Agent: Create adaptive MCQs (easy/medium/hard)
4. Planner Agent: Build revision schedules
5. Chat Agent: Answer doubts from PDF context
```

## 📁 Project Structure

```
vectortutor/
├── app.py                  # Streamlit UI (single-page modern interface)
├── agents/
│   ├── reader_agent.py     # PDF extraction & structuring
│   ├── flashcard_agent.py  # Flashcard generation
│   ├── quiz_agent.py       # Quiz question generation
│   ├── planner_agent.py    # Revision plan creation
│   └── chat_agent.py       # Q&A and summarization
├── utils/
│   ├── groq_client.py      # Groq API wrapper
│   ├── memory.py           # Knowledge Memory Module (SQLite)
│   └── pdf_utils.py        # PDF text extraction
├── .env                    # Environment variables (API key)
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🚀 Installation

### Prerequisites

- Python 3.9 or higher
- Groq API key ([Get one here](https://console.groq.com/))

### Setup Steps

1. **Clone or download this repository**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   - Copy `env.example` to `.env`
   - Add your Groq API key:
     ```
     GROQ_API_KEY=your_actual_api_key_here
     ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser**
   - The app will automatically open at `http://localhost:8501`

## 📖 Usage Guide

### 1. Upload & Read PDF
- Navigate to "📄 Upload & Read PDF" page
- Upload a PDF file
- Click "Process PDF" to extract and structure content
- The Reader Agent will analyze and organize the content

### 2. Generate Flashcards
- Go to "🎴 Flashcards" page
- Select a document
- Choose number of flashcards and optional topic filter
- Click "Generate Flashcards"
- Study with show/hide answer mode

### 3. Take Quizzes
- Visit "📝 Quizzes" page
- Select a document and difficulty level
- Generate quiz questions
- Answer the questions and submit to see your score
- Performance is automatically tracked

### 4. Create Revision Plans
- Open "📅 Revision Planner" page
- Select a document
- Set days until exam and hours per day
- Optionally specify focus topics
- Generate a personalized revision schedule

### 5. Chat & Ask Questions
- Go to "💬 Chat & Doubts" page
- Select a document
- Ask questions about the content
- Get AI-powered answers based on the document
- Generate summaries of your notes

### 6. Track Performance
- Check "📊 Performance & Summary" page
- View quiz accuracy and statistics
- See recommendations based on your performance
- Monitor your learning progress

## 🛠️ Tech Stack

- **Python 3.9+**: Core programming language
- **Streamlit**: Web UI framework
- **Groq API**: AI model (llama-3.3-70b-versatile)
- **PyMuPDF (fitz)**: PDF text extraction
- **SQLite**: Knowledge Memory Module for data persistence
- **JSON**: Data serialization for plans and structured content

## 🔧 Configuration

### Groq API Model
The application uses `llama-3.3-70b-versatile` model by default. You can modify this in `utils/groq_client.py`:

```python
self.model = "llama-3.3-70b-versatile"
```

### Database Location
The SQLite database is created as `vectortutor.db` in the project root. You can change this in `utils/memory.py`:

```python
def __init__(self, db_path: str = "vectortutor.db"):
```

## 📝 Notes

- **PDF Size**: Very large PDFs may be truncated during processing. The system processes the first ~15,000 characters for structuring.
- **API Limits**: Be mindful of Groq API rate limits and usage quotas.
- **Data Persistence**: All data is stored locally in SQLite. The database persists between sessions.

## 🐛 Troubleshooting

### "GROQ_API_KEY not found"
- Make sure you've created a `.env` file with your API key
- Verify the key is correct and has no extra spaces

### "Error extracting PDF text"
- Ensure the PDF is not password-protected
- Check that PyMuPDF is properly installed
- Try with a different PDF file

### Import errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Verify you're using Python 3.9 or higher

## 📄 License

This project is open source and available for educational purposes.

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [Groq](https://groq.com/) API
- PDF processing with [PyMuPDF](https://pymupdf.readthedocs.io/)

---

**Happy Studying! 📚✨**

