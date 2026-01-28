import os
import requests
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv

# ================================
# NewsGenie - Streamlit App
# ================================
# This file provides a simple Streamlit-based UI for interacting with
# the project. It supports fetching top headlines for categories using
# NewsAPI (if NEWSAPI_KEY is provided) and stores per-session history
# using Streamlit's session_state.

# ================================
# 6. Streamlit Frontend
# ================================
# User interface is designed for ease of use
# User enter queries or select news categories via text input.
# UI improvements include displaying previous interactions.

# Load environment and check API availability
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

OPENAI_AVAILABLE = bool(OPENAI_API_KEY)
TAVILY_AVAILABLE = bool(TAVILY_API_KEY)
NEWS_AVAILABLE = bool(NEWS_API_KEY)

if not OPENAI_AVAILABLE:
    st.sidebar.warning("OPENAI_API_KEY not set — using mock assistant.")
if not TAVILY_AVAILABLE:
    st.sidebar.info("TAVILY_API_KEY not set — web search will use mock results.")
if not NEWS_AVAILABLE:
    st.sidebar.info("NEWS_API_KEY not set — news will use sample headlines.")

# Default page size for news
max_articles = 5

# Try to import optional libraries
try:
    from newsapi import NewsApiClient
except Exception:
    NewsApiClient = None

try:
    from langchain_openai import ChatOpenAI
except Exception:
    ChatOpenAI = None

try:
    from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
except Exception:
    TavilySearchAPIWrapper = None

try:
    from langgraph.graph import StateGraph
    from langgraph.prebuilt import ToolNode, tools_condition
    from langgraph.graph.message import add_messages
    from langgraph.checkpoint.memory import MemorySaver
except Exception:
    StateGraph = None
    ToolNode = None
    tools_condition = None
    MemorySaver = None

# Implement news and search helpers with graceful fallbacks

def get_news(category: str) -> list:
    """Return list of article dicts. Uses NewsAPI if available else mock headlines."""
    if NEWS_AVAILABLE and NewsApiClient is not None:
        try:
            client = NewsApiClient(api_key=NEWS_API_KEY)
            resp = client.get_top_headlines(category=category, language='en', page_size=max_articles)
            return resp.get('articles', [])
        except Exception as e:
            print("NewsAPI fetch failed:", e)
    # mock
    return [{"title": f"Sample {category.title()} Headline {i+1}", "source": {"name": "NewsGenie"}, "url": ""} for i in range(max_articles)]


def search_web(query: str, max_results=5) -> list:
    """Return search results from Tavily if available, else mock results."""
    if TAVILY_AVAILABLE and TavilySearchAPIWrapper is not None:
        try:
            wrapper = TavilySearchAPIWrapper(tavily_api_key=TAVILY_API_KEY)
            return wrapper.raw_results(query=query, max_results=max_results, search_depth='advanced', include_answer=False, include_raw_content=True)
        except Exception as e:
            print("Tavily search failed:", e)
    return [{"title": f"Mock result for {query} - {i+1}", "link": ""} for i in range(max_results)]

# Initialize AI assistant or mock
class MockAssistant:
    def invoke(self, messages):
        last = messages[-1]['content'] if messages else ''
        return {"content": f"(Mock) Answer to: {last}"}

    def __call__(self, messages):
        return self.invoke(messages)

if ChatOpenAI is not None and OPENAI_AVAILABLE:
    try:
        ai_assistant = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, openai_api_key=OPENAI_API_KEY)
    except Exception as e:
        print("Failed to init ChatOpenAI:", e)
        ai_assistant = MockAssistant()
else:
    ai_assistant = MockAssistant()

# Assistant tools
assistant_tools = [search_web, get_news]

# Bind tools if possible, else provide a simple wrapper
if hasattr(ai_assistant, 'bind_tools'):
    try:
        ai_with_tools = ai_assistant.bind_tools(assistant_tools)
    except Exception:
        ai_with_tools = ai_assistant
else:
    class ToolWrapper:
        def __init__(self, assistant, tools):
            self.assistant = assistant
            self.tools = tools

        def invoke(self, messages):
            content = messages[-1]['content'] if messages else ''
            cats = ["business","entertainment","general","health","science","sports","technology"]
            for c in cats:
                if c in content.lower():
                    articles = get_news(c)
                    text = "\n\n".join([f"- {a.get('title')} ({(a.get('source') or {}).get('name','')})" for a in articles])
                    return {"content": f"Top {c.title()} headlines:\n\n{text}"}
            return self.assistant.invoke(messages) if hasattr(self.assistant, 'invoke') else {"content": f"(Mock) Answer to: {content}"}

    ai_with_tools = ToolWrapper(ai_assistant, assistant_tools)

# Try to compile a LangGraph agent if available
news_agent = None
if StateGraph is not None:
    try:
        class ConversationState(dict):
            pass

        news_graph = StateGraph(ConversationState)
        def generate_response(state):
            messages = state['dialogue_history']
            return {'dialogue_history': [ai_with_tools.invoke(messages)]}
        news_graph.add_node('ai_response', generate_response)
        if ToolNode is not None:
            tool_node = ToolNode(tools=assistant_tools)
            news_graph.add_node('news_tool', tool_node)
            news_graph.add_conditional_edges('ai_response', tools_condition, ['news_tool', '__end__'])
        news_graph.set_entry_point('ai_response')
        news_agent = news_graph.compile()
    except Exception as e:
        print('LangGraph compile failed:', e)
        news_agent = None

# Improved process_user_request that uses agent -> ai_with_tools -> ai_assistant fallbacks

def process_user_request(user_query, session_id, category=None):
    timestamp = datetime.utcnow().isoformat(timespec='seconds') + 'Z'
    try:
        # If a category is provided, prefer fetching news directly
        categories = ["business","entertainment","general","health","science","sports","technology"]
        if category and category.lower() in categories:
            articles = get_news(category.lower())
            formatted = "\n\n".join([f"- {a.get('title')} ({(a.get('source') or {}).get('name','')})" for a in articles])
            response = f"Top {category.title()} headlines:\n\n{formatted}"
        else:
            # Try LangGraph agent streaming if available
            if news_agent is not None and MemorySaver is not None:
                try:
                    with MemorySaver.from_conn_string('news_session.db') as session_store:
                        session_agent = news_agent.compile(checkpointer=session_store)
                        events = session_agent.stream({'dialogue_history': [{'role':'user','content': user_query}]}, {'configurable': {'session_id': session_id}}, stream_mode='values')
                        last = None
                        for ev in events:
                            last = ev
                        if last:
                            response = last['dialogue_history'][-1]['content']
                        else:
                            response = '(Agent) No response from agent stream.'
                except Exception as e:
                    print('LangGraph runtime failed:', e)
                    # fall through to ai_with_tools
                    result = ai_with_tools.invoke([{'role':'user','content': user_query}])
                    response = result.get('content') if isinstance(result, dict) else str(result)
            else:
                # Directly use ai_with_tools or ai_assistant
                try:
                    result = ai_with_tools.invoke([{'role':'user','content': user_query}])
                    response = result.get('content') if isinstance(result, dict) else str(result)
                except Exception:
                    try:
                        resp = ai_assistant([{'role':'user','content': user_query}]) if hasattr(ai_assistant, '__call__') else ai_assistant.invoke([{'role':'user','content': user_query}])
                        response = resp.get('content') if isinstance(resp, dict) else str(resp)
                    except Exception as e:
                        response = f'(Fallback) Processed query: {user_query}'

        # Save to session history
        entry = {"time": timestamp, "session": session_id, "query": user_query or (category or ''), "category": category or '', "response": response}
        if 'history' not in st.session_state:
            st.session_state.history = []
        st.session_state.history.insert(0, entry)
        return response
    except Exception as e:
        return f"Error processing request: {type(e).__name__}: {e}"

# ------------------------
# Streamlit UI (reuse existing layout)
# ------------------------
st.set_page_config(page_title="NewsGenie", layout="wide")
st.title("NewsGenie - AI-Powered News & Information Assistant")

if 'history' not in st.session_state:
    st.session_state.history = []

col1, col2 = st.columns([3, 1])
with col1:
    user_session = st.text_input('Session ID:', value='guest001')
with col2:
    if st.button('Clear History'):
        st.session_state.history = []
        st.success('Session history cleared.')

category = st.selectbox('Or pick a news category:', ['', 'business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology'], index=0)
query_input = st.text_area('Enter your question or news category (leave blank to use the category selector)')

colA, colB = st.columns(2)
with colA:
    if st.button('Submit'):
        if query_input.strip() or category:
            user_query = query_input.strip() if query_input.strip() else category
            response = process_user_request(user_query, user_session, category if category else None)
            st.markdown(f"**Response:**\n\n{response}")
        else:
            st.warning('Please enter a query or select a category.')
with colB:
    if st.button('Get Category News'):
        if category:
            response = process_user_request('', user_session, category)
            st.markdown(f"**Response:**\n\n{response}")
        else:
            st.warning('Please select a category first.')

# Session history display
st.write('## Session History')
if st.session_state.history:
    for i, e in enumerate(st.session_state.history[:20]):
        with st.expander(f"{e['time']} — {e['session']} — {(e['category'] or 'query')}", expanded=(i==0)):
            st.write('**Query:**', e['query'] or '(category request)')
            st.write('**Category:**', e['category'] or '-')
            st.write('**Response:**')
            st.write(e['response'])
else:
    st.info('No history yet. Your recent queries and news updates will appear here.')

