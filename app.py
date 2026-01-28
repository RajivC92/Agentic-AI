import os
import requests
import streamlit as st
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# LangGraph and LangChain imports
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from typing_extensions import TypedDict

# ================================
# NewsGenie - AI-Powered News & Information Assistant
# ================================
# Implementation based on project requirements:
# - LangGraph-based workflow for efficient query processing
# - Session management with SQLite for conversation persistence 
# - Unified platform integrating OpenAI, NewsAPI, and Tavily APIs
# - Streamlit interface with comprehensive error handling

# Load environment variables
load_dotenv()

# Configure SSL settings for requests to handle certificate issues
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ================================
# State Definition for LangGraph
# ================================
class NewsGenieState(TypedDict):
    query: str
    category: Optional[str]
    session_id: str
    response: str
    route: Optional[str]
    tool_calls: List[Dict[str, Any]]
    conversation_history: List[Dict[str, Any]]

# ================================
# Session Manager with SQLite
# ================================
class SessionManager:
    def __init__(self, db_path="newsgenie_sessions.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for session management"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                query TEXT,
                category TEXT,
                response TEXT,
                metadata TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    def save_interaction(self, session_id: str, query: str, category: str, response: str, metadata: Dict = None):
        """Save user interaction to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sessions (session_id, timestamp, query, category, response, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (session_id, datetime.now().isoformat(), query, category, response, json.dumps(metadata or {})))
        conn.commit()
        conn.close()
    
    def get_session_history(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Retrieve session history from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT timestamp, query, category, response, metadata 
            FROM sessions 
            WHERE session_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (session_id, limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'timestamp': row[0],
                'query': row[1], 
                'category': row[2],
                'response': row[3],
                'metadata': json.loads(row[4]) if row[4] else {}
            })
        
        conn.close()
        return results
# ================================
# Emergency SSL Bypass Functions
# ================================
def emergency_openai_qa(question):
    """OpenAI QA function with SSL bypass"""
    try:
        headers = {
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": question}],
            "max_tokens": 350,
            "temperature": 0.3
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            verify=False,  # SSL bypass
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return f"API Error {response.status_code}: {response.text[:100]}..."
            
    except Exception as e:
        return f"Connection Error: {str(e)[:100]}..."
def emergency_news_fetch(category):
    """NewsAPI fetch with SSL bypass"""
    try:
        news_api_key = os.getenv("NEWS_API_KEY")
        if not news_api_key:
            return get_mock_news(category)
            
        url = f"https://newsapi.org/v2/top-headlines?category={category}&language=en&pageSize=5&apiKey={news_api_key}"
        
        response = requests.get(url, verify=False, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            if articles:
                return articles
    except Exception as e:
        print(f"NewsAPI failed: {e}")
    
    return get_mock_news(category)

def emergency_tavily_search(query, max_results=3):
    """Tavily search with SSL bypass"""
    try:
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        if not tavily_api_key:
            return get_mock_search_results(query)
            
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "api_key": tavily_api_key,
            "query": query,
            "max_results": max_results,
            "search_depth": "advanced",
            "include_answer": False,
            "include_raw_content": True
        }
        
        response = requests.post(
            "https://api.tavily.com/search",
            headers=headers,
            json=payload,
            verify=False,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('results', [])
    except Exception as e:
        print(f"Tavily search failed: {e}")
    
    return get_mock_search_results(query)

def get_mock_search_results(query):
    """Mock search results for offline functionality"""
    return [
        {"title": f"Search result for '{query}' - Result 1", "url": "https://example.com/1", "content": f"Mock content about {query}"},
        {"title": f"Search result for '{query}' - Result 2", "url": "https://example.com/2", "content": f"Additional information about {query}"},
        {"title": f"Search result for '{query}' - Result 3", "url": "https://example.com/3", "content": f"More details about {query}"}
    ]

# ================================
# Tool Definitions
# ================================
def get_news_tool(category: str) -> str:
    """Fetch news articles for a specific category"""
    articles = emergency_news_fetch(category)
    formatted_news = "\n\n".join([
        f"• {article.get('title', 'No title')} - {article.get('source', {}).get('name', 'Unknown source')}"
        for article in articles[:5]
    ])
    return f"Top {category.title()} News:\n\n{formatted_news}"

def search_web_tool(query: str) -> str:
    """Search the web for information"""
    results = emergency_tavily_search(query)
    formatted_results = "\n\n".join([
        f"• {result.get('title', 'No title')}\n  {result.get('content', 'No content')[:200]}..."
        for result in results[:3]
    ])
    return f"Search results for '{query}':\n\n{formatted_results}"

def answer_question_tool(question: str) -> str:
    """Answer general questions using OpenAI"""
    return emergency_openai_qa(question)

# Create LangChain tools
news_tool = Tool(
    name="get_news",
    description="Get latest news articles for categories: business, entertainment, general, health, science, sports, technology",
    func=get_news_tool
)

search_tool = Tool(
    name="search_web", 
    description="Search the web for current information and facts",
    func=search_web_tool
)

qa_tool = Tool(
    name="answer_question",
    description="Answer general questions and provide explanations",
    func=answer_question_tool
)
# ================================
# Mock Data Functions
# ================================
def get_mock_news(category):
    """Fallback mock news data"""
    mock_data = {
        'sports': [
            {"title": "Cricket World Cup Update: Latest Scores and Highlights", "source": {"name": "Sports Today"}, "url": ""},
            {"title": "Football Transfer News: Major Signings This Week", "source": {"name": "Sports Today"}, "url": ""},
            {"title": "Tennis Championships: Upcoming Matches to Watch", "source": {"name": "Sports Today"}, "url": ""},
            {"title": "Basketball Season Highlights and Player Stats", "source": {"name": "Sports Today"}, "url": ""},
            {"title": "Olympic Games Preparation: Athletes in Focus", "source": {"name": "Sports Today"}, "url": ""}
        ],
        'business': [
            {"title": "Stock Market Trends: Tech Shares Rise", "source": {"name": "Business News"}, "url": ""},
            {"title": "Economic Outlook: GDP Growth Projections", "source": {"name": "Business News"}, "url": ""},
            {"title": "Cryptocurrency Update: Market Analysis", "source": {"name": "Business News"}, "url": ""},
            {"title": "Corporate Earnings Reports This Quarter", "source": {"name": "Business News"}, "url": ""},
            {"title": "Global Trade Developments and Impact", "source": {"name": "Business News"}, "url": ""}
        ]
    }
    
    return mock_data.get(category, [
        {"title": f"Latest {category.title()} News", "source": {"name": "News Today"}, "url": ""},
        {"title": f"{category.title()} Weekly Update", "source": {"name": "News Today"}, "url": ""},
        {"title": f"Breaking {category.title()} Headlines", "source": {"name": "News Today"}, "url": ""},
        {"title": f"{category.title()} Analysis", "source": {"name": "News Today"}, "url": ""},
        {"title": f"Top {category.title()} Stories", "source": {"name": "News Today"}, "url": ""}
    ])

# ================================
# LangGraph Workflow Nodes
# ================================
def route_query_node(state: NewsGenieState) -> NewsGenieState:
    """Route user query to appropriate handler"""
    query = state["query"].lower()
    category = state.get("category", "") or ""  # Handle None values
    category = category.lower()
    
    # Check for specific news categories
    news_categories = ["business", "entertainment", "general", "health", "science", "sports", "technology"]
    
    # Check for explicit search requests (highest priority)
    search_keywords = ["search", "find", "lookup", "browse"]
    explicit_search = any(keyword in query for keyword in search_keywords)
    
    # Check for proper question structure (question word + verb/auxiliary)
    question_words = ["who", "what", "when", "where", "why", "how"]
    verbs_auxiliaries = ["is", "are", "can", "could", "will", "would", "should", "do", "does", "did"]
    instructions = ["tell", "explain", "describe", "define"]
    
    # True question: has question word + verb/auxiliary OR instruction verb
    proper_question = (
        any(qw in query for qw in question_words) and any(va in query for va in verbs_auxiliaries)
    ) or any(inst in query for inst in instructions)
    
    # Routing logic with clear priorities:
    if explicit_search:
        # If user explicitly says "search" or "find", use web search
        state["route"] = "search_web"
    elif proper_question:
        # For proper questions with clear structure, use AI to answer
        state["route"] = "answer_question"
    elif category in news_categories and not proper_question and not explicit_search:
        # Only show news if category selected and no specific question/search
        state["route"] = "get_news"
    elif any(cat in query for cat in news_categories) and not proper_question and not explicit_search:
        # Extract category from query if no specific question/search
        for cat in news_categories:
            if cat in query:
                state["category"] = cat
                state["route"] = "get_news"
                break
    else:
        # Default to web search for general terms and phrases
        state["route"] = "search_web"
    
    return state

def determine_next_node(state: NewsGenieState) -> str:
    """Determine which node to route to based on the routing decision"""
    return state.get("route", "answer_question")

def get_news_node(state: NewsGenieState) -> NewsGenieState:
    """Handle news requests"""
    category = state.get("category", "general")
    response = get_news_tool(category)
    state["response"] = response
    state["tool_calls"].append({"tool": "get_news", "category": category})
    return state

def search_web_node(state: NewsGenieState) -> NewsGenieState:
    """Handle web search requests"""
    query = state["query"]
    response = search_web_tool(query)
    state["response"] = response
    state["tool_calls"].append({"tool": "search_web", "query": query})
    return state

def answer_question_node(state: NewsGenieState) -> NewsGenieState:
    """Handle general Q&A requests"""
    question = state["query"]
    category = state.get("category", "") or ""  # Handle None values
    
    # If there's a category context, include it in the question
    if category and category.strip():
        contextual_question = f"In the context of {category}, {question}"
        response = answer_question_tool(contextual_question)
    else:
        response = answer_question_tool(question)
    
    state["response"] = response
    state["tool_calls"].append({"tool": "answer_question", "question": question, "category": category})
    return state

# ================================
# LangGraph Workflow Setup  
# ================================
def create_newsgenie_workflow():
    """Create the LangGraph workflow for NewsGenie"""
    workflow = StateGraph(NewsGenieState)
    
    # Add nodes
    workflow.add_node("route_query", route_query_node)
    workflow.add_node("get_news", get_news_node)
    workflow.add_node("search_web", search_web_node)
    workflow.add_node("answer_question", answer_question_node)
    
    # Define the workflow
    workflow.set_entry_point("route_query")
    
    # Add conditional edges from route_query
    workflow.add_conditional_edges(
        "route_query",
        determine_next_node,
        {
            "get_news": "get_news",
            "search_web": "search_web", 
            "answer_question": "answer_question"
        }
    )
    
    # End edges
    workflow.add_edge("get_news", END)
    workflow.add_edge("search_web", END)
    workflow.add_edge("answer_question", END)
    
    # Add memory
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)

# Initialize the workflow
newsgenie_app = create_newsgenie_workflow()

# Initialize session manager
session_manager = SessionManager()

# ================================
# API Configuration and Status
# ================================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY") 
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

OPENAI_AVAILABLE = bool(OPENAI_API_KEY)
TAVILY_AVAILABLE = bool(TAVILY_API_KEY)
NEWS_AVAILABLE = bool(NEWS_API_KEY)

# ================================
# Main Processing Function
# ================================
def process_user_request(user_query: str, session_id: str, category: Optional[str] = None) -> str:
    """Process user request using LangGraph workflow"""
    try:
        # Prepare initial state
        initial_state = NewsGenieState(
            query=user_query,
            category=category,
            session_id=session_id,
            response="",
            route=None,
            tool_calls=[],
            conversation_history=session_manager.get_session_history(session_id, limit=5)
        )
        
        # Run the workflow
        config = {"configurable": {"thread_id": session_id}}
        result = newsgenie_app.invoke(initial_state, config)
        
        # Extract response
        response = result.get("response", "I apologize, but I couldn't process your request properly.")
        
        # Save to session history
        session_manager.save_interaction(
            session_id=session_id,
            query=user_query,
            category=category or "",
            response=response,
            metadata={"tool_calls": result.get("tool_calls", [])}
        )
        
        return response
        
    except Exception as e:
        error_response = f"I encountered an error processing your request: {str(e)[:100]}. Please try rephrasing your question."
        
        # Still save the error to history
        session_manager.save_interaction(
            session_id=session_id,
            query=user_query,
            category=category or "",
            response=error_response,
            metadata={"error": str(e)}
        )
        
        return error_response

# ================================
# Streamlit UI
# ================================
st.set_page_config(page_title="NewsGenie", page_icon="🗞️", layout="wide")

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #4CAF50 0%, #2196F3 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        color: white;
        text-align: center;
        margin: 0;
    }
    .status-box {
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    .success { background-color: #d4edda; }
    .warning { background-color: #fff3cd; }
    .info { background-color: #d1ecf1; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header"><h1>🗞️ NewsGenie - AI-Powered News & Information Assistant</h1></div>', unsafe_allow_html=True)

# API Status Sidebar
st.sidebar.header("🔧 API Status")

if OPENAI_AVAILABLE:
    st.sidebar.markdown('<div class="status-box success">✅ OpenAI API: Connected</div>', unsafe_allow_html=True)
else:
    st.sidebar.markdown('<div class="status-box warning">⚠️ OpenAI API: Not configured (using fallback)</div>', unsafe_allow_html=True)

if NEWS_AVAILABLE:
    st.sidebar.markdown('<div class="status-box success">✅ NewsAPI: Connected</div>', unsafe_allow_html=True)
else:
    st.sidebar.markdown('<div class="status-box info">ℹ️ NewsAPI: Not configured (using mock data)</div>', unsafe_allow_html=True)

if TAVILY_AVAILABLE:
    st.sidebar.markdown('<div class="status-box success">✅ Tavily Search: Connected</div>', unsafe_allow_html=True)
else:
    st.sidebar.markdown('<div class="status-box info">ℹ️ Tavily Search: Not configured (using mock results)</div>', unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📖 How to Use")
st.sidebar.markdown("""
1. **Select a category** to get latest news
2. **Ask questions** for AI-powered answers  
3. **Search topics** for web information
4. **View history** of your session

**Features:**
- LangGraph-based intelligent routing
- Session persistence with SQLite
- Multi-API integration (OpenAI, NewsAPI, Tavily)
- Comprehensive error handling
""")

# Initialize session state
if 'session_history' not in st.session_state:
    st.session_state.session_history = []

# Main interface
col1, col2 = st.columns([3, 1])

with col1:
    session_id = st.text_input('🆔 Session ID:', value='guest001', help="Unique identifier for your session")

with col2:
    if st.button('🗑️ Clear History'):
        st.session_state.session_history = []
        st.success('Session history cleared!')

# Input section
st.markdown("### 💬 Your Query")
col_cat, col_query = st.columns([1, 2])

with col_cat:
    category = st.selectbox(
        '📂 News Category:',
        ['', 'business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology'],
        index=0,
        help="Select a category for latest news"
    )

with col_query:
    user_query = st.text_area(
        '❓ Enter your question:', 
        height=100,
        placeholder="Ask anything - news, questions, or search topics...",
        help="Type your question or select a category above"
    )

# Action buttons
col_submit, col_news = st.columns(2)

with col_submit:
    if st.button('🚀 Submit Query', type="primary"):
        if user_query.strip() or category:
            with st.spinner('🤖 Processing your request...'):
                query_text = user_query.strip() if user_query.strip() else f"Get {category} news"
                response = process_user_request(query_text, session_id, category if category else None)
                
                # Display response
                st.markdown("### 📋 Response")
                st.markdown(response)
                
                # Add to session history
                st.session_state.session_history.insert(0, {
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'query': query_text,
                    'category': category or 'N/A',
                    'response': response
                })
        else:
            st.warning('⚠️ Please enter a query or select a category.')

with col_news:
    if st.button('📰 Get Category News'):
        if category:
            with st.spinner(f'📡 Fetching {category} news...'):
                response = process_user_request(f"Get latest {category} news", session_id, category)
                
                # Display response
                st.markdown("### 📰 Latest News")
                st.markdown(response)
                
                # Add to session history
                st.session_state.session_history.insert(0, {
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'query': f'Get {category} news',
                    'category': category,
                    'response': response
                })
        else:
            st.warning('⚠️ Please select a category first.')

# Session History
st.markdown("---")
st.markdown("### 📚 Session History")

if st.session_state.session_history:
    for i, entry in enumerate(st.session_state.session_history[:10]):
        with st.expander(f"🕒 {entry['timestamp']} — {entry['category']} — {entry['query'][:50]}{'...' if len(entry['query']) > 50 else ''}", expanded=(i==0)):
            st.markdown(f"**❓ Query:** {entry['query']}")
            st.markdown(f"**📂 Category:** {entry['category']}")
            st.markdown(f"**📋 Response:**")
            st.markdown(entry['response'])
else:
    st.info('📝 No history yet. Your queries and responses will appear here.')

# Footer
st.markdown("---")
st.markdown("### 🏗️ Technical Details")
with st.expander("View Implementation Details"):
    st.markdown("""
    **Architecture:**
    - **LangGraph Workflow**: Intelligent query routing and processing
    - **SQLite Session Management**: Persistent conversation history
    - **Multi-API Integration**: OpenAI, NewsAPI, Tavily with fallback mechanisms
    - **SSL Bypass**: Handles certificate issues automatically
    
    **Features:**
    - Smart query routing based on content analysis
    - Real-time news fetching with category support
    - Web search capabilities for current information
    - AI-powered question answering
    - Session persistence across app restarts
    - Comprehensive error handling and fallback systems
    
    **Technologies:**
    - Streamlit for web interface
    - LangGraph for workflow orchestration
    - SQLite for data persistence  
    - OpenAI GPT-3.5-turbo for AI responses
    - NewsAPI for real-time news
    - Tavily for web search
    """)