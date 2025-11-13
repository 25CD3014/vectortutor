"""
VectorTutor - Streamlit App
Modern single-page UI with all features accessible from home
"""
import streamlit as st
import os
from pathlib import Path
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.groq_client import GroqClient
from utils.memory import KnowledgeMemory
from agents.reader_agent import ReaderAgent
from agents.flashcard_agent import FlashcardAgent
from agents.quiz_agent import QuizAgent
from agents.planner_agent import PlannerAgent
from agents.chat_agent import ChatAgent


# Page configuration
st.set_page_config(
    page_title="VectorTutor - AI Learning Companion",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern UI
st.markdown("""
<style>
    .stApp {
        background-color: #000000;
    }
    .main-header {
        background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
        padding: 2rem;
        border-radius: 15px;
        color: #ffa500;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(255, 165, 0, 0.2);
        border: 2px solid #ffa500;
    }
    .feature-card {
        background: #1a1a1a;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(255, 165, 0, 0.1);
        margin-bottom: 1.5rem;
        border-left: 4px solid #ffa500;
        transition: transform 0.2s;
    }
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 165, 0, 0.3);
        border-left-color: #ffd700;
    }
    .stat-card {
        background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: #ffa500;
        text-align: center;
        box-shadow: 0 4px 15px rgba(255, 165, 0, 0.2);
        border: 2px solid #ffa500;
    }
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0.5rem 0;
        color: #ffa500;
    }
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
        color: #ffd700;
    }
    .stButton>button {
        background: linear-gradient(135deg, #ffa500 0%, #ff8c00 100%);
        color: #000000;
        border: 2px solid #ffa500;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 700;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        background: linear-gradient(135deg, #ffd700 0%, #ffa500 100%);
        box-shadow: 0 5px 15px rgba(255, 165, 0, 0.5);
        border-color: #ffd700;
        color: #000000;
    }
    .section-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #ffa500;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #ffa500;
    }
    .agent-badge {
        display: inline-block;
        background: #ffa500;
        color: #000000;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        margin: 0.2rem;
        border: 1px solid #ffd700;
        font-weight: 600;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #000000 0%, #1a1a1a 100%);
    }
    .stExpander {
        border: 2px solid #ffa500;
        border-radius: 8px;
        background-color: #1a1a1a;
    }
    .stExpander label {
        color: #ffa500;
        font-weight: 700;
    }
    .stExpander label:hover {
        color: #ffd700;
    }
    .stSelectbox label, .stTextInput label, .stNumberInput label {
        color: #ffa500;
        font-weight: 600;
    }
    .stMarkdown {
        color: #ffffff;
    }
    .stInfo {
        background-color: #1a1a1a;
        border-left: 4px solid #ffa500;
    }
    .stSuccess {
        background-color: #1a1a1a;
        border-left: 4px solid #ffa500;
        color: #ffa500;
    }
    .stWarning {
        background-color: #1a1a1a;
        border-left: 4px solid #ffa500;
        color: #ffa500;
    }
    .stError {
        background-color: #1a1a1a;
        border-left: 4px solid #ff0000;
        color: #ff6666;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #ffa500;
    }
    p, div, span {
        color: #ffffff;
    }
    .stMetric {
        background-color: #1a1a1a;
    }
    .stMetric label {
        color: #ffd700;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #ffa500;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "groq_client" not in st.session_state:
    try:
        st.session_state.groq_client = GroqClient()
    except Exception as e:
        st.error(f"Error initializing Groq client: {str(e)}")
        st.stop()

if "memory" not in st.session_state:
    st.session_state.memory = KnowledgeMemory()

if "reader_agent" not in st.session_state:
    st.session_state.reader_agent = ReaderAgent(
        st.session_state.groq_client, 
        st.session_state.memory
    )

if "flashcard_agent" not in st.session_state:
    st.session_state.flashcard_agent = FlashcardAgent(
        st.session_state.groq_client,
        st.session_state.memory
    )

if "quiz_agent" not in st.session_state:
    st.session_state.quiz_agent = QuizAgent(
        st.session_state.groq_client,
        st.session_state.memory
    )

if "planner_agent" not in st.session_state:
    st.session_state.planner_agent = PlannerAgent(
        st.session_state.groq_client,
        st.session_state.memory
    )

if "chat_agent" not in st.session_state:
    st.session_state.chat_agent = ChatAgent(
        st.session_state.groq_client,
        st.session_state.memory
    )

# Initialize session state for UI
if "active_section" not in st.session_state:
    st.session_state.active_section = None
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# Sidebar - Hidden by default, only for quick navigation
with st.sidebar:
    st.markdown("### VectorTutor Navigation")
    nav_option = st.selectbox(
        "Jump to Section",
        ["🏠 Home", "📄 Upload PDF", "🎴 Flashcards", "📝 Quizzes", "📅 Planner", "💬 Chat", "📊 Performance"],
        index=0,
        label_visibility="collapsed"
    )
    if nav_option != "🏠 Home":
        st.session_state.active_section = nav_option

# Main Header
st.markdown("""
<div class="main-header">
    <h1 style="margin: 0; font-size: 3rem;">VectorTutor</h1>
    <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; opacity: 0.95;">Your AI-Powered Learning Companion</p>
    <div style="margin-top: 1rem;">
        <span class="agent-badge">Reader Agent</span>
        <span class="agent-badge">Flashcard Agent</span>
        <span class="agent-badge">Quiz Agent</span>
        <span class="agent-badge">Planner Agent</span>
        <span class="agent-badge">Chat Agent</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Statistics Dashboard
documents = st.session_state.memory.get_all_documents()
flashcards = st.session_state.memory.get_flashcards()
quizzes = st.session_state.memory.get_quizzes()
performance = st.session_state.memory.get_performance_stats()

st.markdown('<div class="section-header">📊 Your Dashboard</div>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">Documents</div>
        <div class="stat-number">{len(documents)}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">Flashcards</div>
        <div class="stat-number">{len(flashcards)}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">Quiz Questions</div>
        <div class="stat-number">{len(quizzes)}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">Quiz Accuracy</div>
        <div class="stat-number">{performance['accuracy']}%</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Feature Sections with Expanders
# 1. Upload & Read PDF
with st.expander("📄 **Upload & Read PDF** - Extract and structure your documents", expanded=st.session_state.active_section == "📄 Upload PDF"):
    st.session_state.active_section = None  # Reset after opening
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"], key="pdf_uploader")
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        process_btn = st.button("🚀 Process PDF", type="primary", use_container_width=True)
    
    if uploaded_file is not None and process_btn:
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        with st.spinner("🔄 Processing PDF with Reader Agent..."):
            try:
                result = st.session_state.reader_agent.process_pdf(temp_path, uploaded_file.name)
                st.success(f"✅ PDF processed successfully! Document ID: {result['document_id']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"**Filename:** {result['filename']}\n\n**Text Length:** {result['text_length']:,} characters")
                with col2:
                    if result['metadata']:
                        meta = result['metadata']
                        st.info(f"**Pages:** {meta.get('page_count', 'N/A')}\n\n**Author:** {meta.get('author', 'N/A')}")
                
                if result.get('structured_content'):
                    st.markdown("---")
                    st.markdown("#### 📑 Structured Content")
                    structured = result['structured_content']
                    if structured.get('structured_analysis'):
                        with st.container():
                            st.markdown("**Analysis:**")
                            st.write(structured['structured_analysis'])
                    if structured.get('topics'):
                        st.markdown("**Main Topics:**")
                        for topic in structured['topics']:
                            st.write(f"• {topic}")
                
                st.session_state.current_document_id = result['document_id']
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error processing PDF: {str(e)}")
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
    
    # Document List
    if documents:
        st.markdown("#### 📚 Your Documents")
        for doc in documents[:5]:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**{doc['filename']}**")
                with col2:
                    st.caption(f"ID: {doc['id']}")
                with col3:
                    if st.button(f"Select", key=f"select_doc_{doc['id']}"):
                        st.session_state.current_document_id = doc['id']
                        st.success(f"✅ Selected: {doc['filename']}")
                        st.rerun()

# 2. Flashcards
with st.expander("🎴 **Flashcards** - Generate Q&A flashcards for active recall", expanded=st.session_state.active_section == "🎴 Flashcards"):
    st.session_state.active_section = None
    
    if not documents:
        st.warning("⚠️ Please upload a PDF first!")
    else:
        doc_options = {f"{doc['filename']} (ID: {doc['id']})": doc['id'] for doc in documents}
        selected_doc = st.selectbox("Select Document", list(doc_options.keys()), key="flashcard_doc")
        document_id = doc_options[selected_doc]
        
        col1, col2 = st.columns(2)
        with col1:
            num_flashcards = st.number_input("Number of Flashcards", min_value=1, max_value=50, value=10, key="num_fc")
        with col2:
            topic_filter = st.text_input("Topic Filter (optional)", key="fc_topic")
        
        if st.button("✨ Generate Flashcards", type="primary", key="gen_fc"):
            with st.spinner("🎴 Generating flashcards..."):
                try:
                    flashcards = st.session_state.flashcard_agent.generate_flashcards(
                        document_id, num_flashcards, topic_filter if topic_filter else None
                    )
                    st.success(f"✅ Generated {len(flashcards)} flashcards!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        # Display Flashcards
        st.markdown("---")
        st.markdown("#### 📚 Your Flashcards")
        flashcards_list = st.session_state.flashcard_agent.get_flashcards(document_id)
        
        if flashcards_list:
            study_mode = st.checkbox("📖 Study Mode (Show/Hide Answers)", key="study_mode")
            
            for i, fc in enumerate(flashcards_list):
                with st.container():
                    st.markdown(f"**Flashcard {i+1}**")
                    st.write(f"❓ **Q:** {fc['question']}")
                    
                    if study_mode:
                        if st.button(f"Show Answer", key=f"show_fc_{fc['id']}"):
                            st.session_state[f"show_fc_{fc['id']}"] = True
                        if st.session_state.get(f"show_fc_{fc['id']}", False):
                            st.write(f"✅ **A:** {fc['answer']}")
                    else:
                        st.write(f"✅ **A:** {fc['answer']}")
                    
                    if fc.get('topic'):
                        st.caption(f"📌 Topic: {fc['topic']} | Difficulty: {fc.get('difficulty', 'N/A')}")
                    st.markdown("---")
        else:
            st.info("💡 No flashcards yet. Generate some to get started!")

# 3. Quizzes
with st.expander("📝 **Quizzes** - Test your knowledge with adaptive MCQs", expanded=st.session_state.active_section == "📝 Quizzes"):
    st.session_state.active_section = None
    
    if not documents:
        st.warning("⚠️ Please upload a PDF first!")
    else:
        doc_options = {f"{doc['filename']} (ID: {doc['id']})": doc['id'] for doc in documents}
        selected_doc = st.selectbox("Select Document", list(doc_options.keys()), key="quiz_doc")
        document_id = doc_options[selected_doc]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            num_questions = st.number_input("Number of Questions", min_value=1, max_value=30, value=10, key="num_q")
        with col2:
            difficulty = st.selectbox("Difficulty", ["Mixed", "Easy", "Medium", "Hard"], key="quiz_diff")
        with col3:
            topic_filter = st.text_input("Topic Filter (optional)", key="quiz_topic")
        
        if st.button("🎯 Generate Quiz", type="primary", key="gen_quiz"):
            with st.spinner("📝 Generating quiz..."):
                try:
                    diff = None if difficulty == "Mixed" else difficulty.lower()
                    quizzes = st.session_state.quiz_agent.generate_quiz(
                        document_id, num_questions, diff, topic_filter if topic_filter else None
                    )
                    st.success(f"✅ Generated {len(quizzes)} questions!")
                    st.session_state.current_quiz = quizzes
                    st.session_state.quiz_answers = {}
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        # Take Quiz
        if st.session_state.get('current_quiz'):
            st.markdown("---")
            st.markdown("#### 📝 Take Quiz")
            quiz_to_take = st.session_state.current_quiz
            
            for i, q in enumerate(quiz_to_take):
                st.markdown(f"### Question {i+1}")
                st.write(f"**{q['question']}**")
                
                options = q['options']
                selected = st.radio(
                    "Select your answer:",
                    options,
                    key=f"quiz_{q['id']}",
                    index=None
                )
                
                if selected:
                    selected_index = options.index(selected)
                    st.session_state.quiz_answers[q['id']] = selected_index
                
                st.markdown("---")
            
            if st.button("📤 Submit Quiz", type="primary", key="submit_quiz"):
                score = 0
                total = len(quiz_to_take)
                
                for q in quiz_to_take:
                    user_answer = st.session_state.quiz_answers.get(q['id'])
                    if user_answer is not None:
                        is_correct = st.session_state.quiz_agent.submit_answer(q['id'], user_answer)
                        if is_correct:
                            score += 1
                
                accuracy = (score/total*100) if total > 0 else 0
                st.success(f"🎉 Quiz Complete! Score: **{score}/{total}** ({accuracy:.1f}%)")
                st.session_state.quiz_answers = {}
                st.session_state.current_quiz = None
                st.rerun()

# 4. Revision Planner
with st.expander("📅 **Revision Planner** - Create personalized study schedules", expanded=st.session_state.active_section == "📅 Planner"):
    st.session_state.active_section = None
    
    if not documents:
        st.warning("⚠️ Please upload a PDF first!")
    else:
        doc_options = {f"{doc['filename']} (ID: {doc['id']})": doc['id'] for doc in documents}
        selected_doc = st.selectbox("Select Document", list(doc_options.keys()), key="plan_doc")
        document_id = doc_options[selected_doc]
        
        col1, col2 = st.columns(2)
        with col1:
            days_until_exam = st.number_input("Days Until Exam", min_value=1, max_value=90, value=7, key="days_exam")
        with col2:
            hours_per_day = st.number_input("Hours Per Day", min_value=0.5, max_value=12.0, value=2.0, step=0.5, key="hours_day")
        
        focus_topics = st.text_input("Focus Topics (comma-separated, optional)", key="focus_topics")
        topics_list = [t.strip() for t in focus_topics.split(",") if t.strip()] if focus_topics else None
        
        if st.button("📅 Create Revision Plan", type="primary", key="create_plan"):
            with st.spinner("📅 Creating revision plan..."):
                try:
                    plan = st.session_state.planner_agent.create_revision_plan(
                        document_id, days_until_exam, hours_per_day, topics_list
                    )
                    st.success("✅ Revision plan created successfully!")
                    st.session_state.current_plan = plan
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        # Display Plans
        plans = st.session_state.planner_agent.get_revision_plans(document_id)
        if plans:
            st.markdown("---")
            st.markdown("#### 📅 Your Revision Plans")
            for plan in plans:
                plan_data = plan['plan_data']
                with st.expander(f"📅 {plan_data.get('plan_name', 'Revision Plan')} - {plan['created_at']}"):
                    st.write(f"**Total Days:** {plan_data.get('total_days', 'N/A')} | **Hours/Day:** {plan_data.get('hours_per_day', 'N/A')}")
                    
                    schedule = plan_data.get('schedule', [])
                    for day_plan in schedule:
                        st.markdown(f"**Day {day_plan.get('day', 'N/A')} - {day_plan.get('date', 'N/A')}**")
                        st.write(f"📌 Topics: {', '.join(day_plan.get('topics', []))}")
                        st.write(f"📝 {day_plan.get('notes', 'N/A')}")
                        
                        activities = day_plan.get('activities', [])
                        if activities:
                            for activity in activities:
                                st.write(f"  • {activity.get('type', 'N/A')}: {activity.get('description', 'N/A')} ({activity.get('duration_minutes', 0)} min)")
                        st.markdown("---")
                    
                    tips = plan_data.get('tips', [])
                    if tips:
                        st.markdown("**💡 Tips:**")
                        for tip in tips:
                            st.write(f"  • {tip}")

# 5. Chat & Doubts
with st.expander("💬 **Chat & Doubts** - Ask questions and get AI-powered answers", expanded=st.session_state.active_section == "💬 Chat"):
    st.session_state.active_section = None
    
    if not documents:
        st.warning("⚠️ Please upload a PDF first!")
    else:
        doc_options = {f"{doc['filename']} (ID: {doc['id']})": doc['id'] for doc in documents}
        selected_doc = st.selectbox("Select Document", list(doc_options.keys()), key="chat_doc")
        document_id = doc_options[selected_doc]
        
        st.markdown("#### 💬 Ask a Question")
        
        # Display chat history
        for msg in st.session_state.chat_messages:
            if msg["role"] == "user":
                with st.chat_message("user"):
                    st.write(msg["content"])
            else:
                with st.chat_message("assistant"):
                    st.write(msg["content"])
        
        question = st.chat_input("Ask a question about the document...", key="chat_input")
        
        if question:
            st.session_state.chat_messages.append({"role": "user", "content": question})
            
            with st.spinner("🤔 Thinking..."):
                try:
                    result = st.session_state.chat_agent.answer_question(document_id, question)
                    answer = result["answer"]
                    st.session_state.chat_messages.append({"role": "assistant", "content": answer})
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        st.markdown("---")
        
        # Summarize Notes
        st.markdown("#### 📝 Summarize Notes")
        col1, col2 = st.columns([3, 1])
        with col1:
            focus_topic = st.text_input("Focus Topic (optional)", key="summary_topic")
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("📄 Generate Summary", type="primary", key="gen_summary"):
                with st.spinner("📝 Generating summary..."):
                    try:
                        summary = st.session_state.chat_agent.summarize_notes(
                            document_id, focus_topic if focus_topic else None
                        )
                        st.markdown("#### Summary")
                        st.write(summary)
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

# 6. Performance & Summary
with st.expander("📊 **Performance & Summary** - Track your learning progress", expanded=st.session_state.active_section == "📊 Performance"):
    st.session_state.active_section = None
    
    if not documents:
        st.warning("⚠️ Please upload a PDF first!")
    else:
        doc_options = {f"{doc['filename']} (ID: {doc['id']})": doc['id'] for doc in documents}
        selected_doc = st.selectbox("Select Document", list(doc_options.keys()), key="perf_doc")
        document_id = doc_options[selected_doc]
        
        st.markdown("#### 📈 Performance Statistics")
        
        performance = st.session_state.memory.get_performance_stats(document_id)
        flashcards = st.session_state.memory.get_flashcards(document_id)
        quizzes = st.session_state.memory.get_quizzes(document_id)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Quiz Attempts", performance['total_attempts'])
        with col2:
            st.metric("Correct Answers", performance['correct_attempts'])
        with col3:
            st.metric("Accuracy", f"{performance['accuracy']}%")
        with col2:
            st.metric("Flashcards", len(flashcards))
        
        st.markdown("---")
        st.markdown("#### 💡 Recommendations")
        
        if performance['total_attempts'] == 0:
            st.info("📝 Start taking quizzes to track your performance!")
        elif performance['accuracy'] < 50:
            st.warning("📚 Your accuracy is below 50%. Consider reviewing the material and creating more flashcards.")
        elif performance['accuracy'] < 70:
            st.info("📖 Your accuracy is good! Keep practicing to improve further.")
        else:
            st.success("🎉 Excellent performance! You're mastering the material!")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>Built with ❤️ using Streamlit & Groq API</p>
    <p>VectorTutor - 5-Agent AI Learning System</p>
</div>
""", unsafe_allow_html=True)
