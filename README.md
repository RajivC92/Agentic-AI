# 🗞️ NewsGenie - AI-Powered News & Information Assistant

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![LangGraph](https://img.shields.io/badge/LangGraph-Latest-green.svg)](https://langchain.com/langgraph)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5--turbo-orange.svg)](https://openai.com)

> **A sophisticated AI-powered application that intelligently routes user queries through multiple APIs to provide real-time news, AI-driven answers, and web search results using advanced LangGraph workflows.**

## 🏗️ **Architecture & Design**

### **Core Architecture**
NewsGenie implements a **LangGraph-based workflow orchestration** system that intelligently routes user queries through multiple specialized nodes:

```
User Query → Route Analysis → [News API | OpenAI API | Tavily Search] → Response
```

### **Key Technical Components**

1. **🧠 Custom Query Router Engine**
   - **Custom NLP-based routing logic** with 4-tier priority hierarchies
   - **Rule-based decision tree** for optimal API selection
   - **Pattern matching algorithms** for query classification
   - Supports explicit search commands, structured questions, and general topics

2. **🔄 LangGraph Workflow Orchestration**
   - **StateGraph framework** for workflow execution (not decision making)
   - **Custom routing functions** integrated with LangGraph nodes
   - Memory persistence with `MemorySaver` for conversation context
   - **Conditional edge execution** based on custom routing decisions

3. **💾 Session Management System**
   - SQLite-based conversation persistence
   - User session tracking with comprehensive metadata
   - Historical query analysis and response tracking

4. **🛡️ Robust Error Handling**
   - SSL certificate bypass for enterprise environments
   - API fallback mechanisms with mock data
   - Graceful degradation when services are unavailable

## 🚀 **Features & Capabilities**

### **Multi-Modal Information Retrieval**
- **📰 Real-Time News**: Live headlines from NewsAPI across 7 categories
- **🤖 AI Q&A**: Context-aware responses using OpenAI GPT-3.5-turbo
- **🔍 Web Search**: Current information retrieval via Tavily Search API
- **📊 Session Analytics**: Comprehensive conversation history and analytics

### **Advanced Query Processing**
```python
# Example routing logic
"search AI trends" → Web Search (Tavily)
"explain machine learning" → AI Answer (OpenAI) 
"entertainment news" → News Headlines (NewsAPI)
"who is the superstar in Indian Cinema?" → AI Answer with context
```

### **Enterprise-Ready Features**
- **SSL/TLS Certificate Handling**: Automatic bypass for corporate firewalls
- **API Rate Limiting**: Intelligent request management
- **Offline Fallbacks**: Mock data when APIs are unavailable
- **Multi-Environment Support**: Dev/staging/production configurations

## 🛠️ **Technology Stack**

### **Backend Framework**
- **Streamlit**: Modern web application framework
- **LangGraph**: Advanced workflow orchestration
- **SQLite**: Lightweight database for session management

### **AI & ML Integration**
- **OpenAI GPT-3.5-turbo**: Natural language processing
- **LangChain**: AI framework and tool integration
- **Custom NLP**: Query classification and routing logic

### **External APIs**
- **NewsAPI**: Real-time news aggregation
- **Tavily Search**: Web search and information retrieval
- **OpenAI API**: Conversational AI capabilities

### **Security & Infrastructure**
- **SSL Bypass**: Enterprise firewall compatibility
- **Environment Variables**: Secure API key management
- **Error Logging**: Comprehensive error tracking

## 📦 **Installation & Setup**

### **Prerequisites**
```bash
Python 3.8+
pip package manager
API Keys (optional - works with fallbacks)
```

### **Quick Start**
```bash
# Clone the repository
git clone <repository-url>
cd NewsGenie

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (optional)
cp .env.example .env
# Add your API keys to .env file

# Run the application
streamlit run app.py
```

### **Environment Configuration**
```bash
# .env file (optional)
OPENAI_API_KEY=your_openai_key_here
NEWS_API_KEY=your_newsapi_key_here
TAVILY_API_KEY=your_tavily_key_here
```

## 🎯 **Usage Examples**

### **News Retrieval**
```
Category: Sports
Query: "latest cricket updates"
Result: Live sports headlines from trusted sources
```

### **AI Question Answering**
```
Query: "explain quantum computing in simple terms"
Result: Detailed AI-generated explanation with context
```

### **Web Search**
```
Query: "search latest AI developments"
Result: Current web search results with summaries
```

### **Contextual Queries**
```
Category: Entertainment
Query: "who is the biggest superstar?"
Result: AI answer with entertainment industry context
```

## 🏆 **Technical Highlights**

### **Custom Routing Algorithm (Not LangGraph Decision Making)**
- **4-tier priority-based decision tree** implemented in Python
- **Custom NLP pattern matching** for query intent detection  
- **Rule-based classification engine** with explicit search detection
- **Context-aware categorization** with intelligent fallback mechanisms

### **LangGraph Integration (Workflow Orchestration)**
- **StateGraph framework** manages workflow execution flow
- **Custom routing functions** (`route_query_node`, `determine_next_node`)
- **Conditional edge routing** executes custom routing decisions
- **Memory management** for conversation persistence

### **State Management**
```python
class NewsGenieState(TypedDict):
    query: str
    category: Optional[str] 
    session_id: str
    response: str
    route: Optional[str]
    tool_calls: List[Dict[str, Any]]
    conversation_history: List[Dict[str, Any]]
```

### **Workflow Orchestration**
```python
# LangGraph workflow with conditional routing
workflow = StateGraph(NewsGenieState)
workflow.add_conditional_edges(
    "route_query",
    determine_next_node,
    {
        "get_news": "get_news",
        "search_web": "search_web", 
        "answer_question": "answer_question"
    }
)
```

## 📊 **Performance Features**

- **⚡ Fast Response Times**: Optimized API calls with timeout handling
- **🔄 Intelligent Caching**: Session-based conversation memory
- **📈 Scalable Architecture**: Stateless design for horizontal scaling
- **🛡️ Error Resilience**: Comprehensive fallback mechanisms

## 🔮 **Future Enhancements**

- **🌐 Multi-language Support**: International news and queries
- **📱 Mobile App**: React Native implementation
- **🔔 Real-time Notifications**: Breaking news alerts
- **📊 Analytics Dashboard**: Usage metrics and insights
- **🤝 Integration APIs**: Third-party system integration
- **🔐 Authentication**: User management and personalization

## 🎨 **User Interface**

- **Modern Streamlit Design**: Clean, responsive interface
- **Real-time Status Indicators**: API connectivity status
- **Interactive Categories**: Dynamic news category selection  
- **Session History**: Conversation timeline with search
- **Error Handling**: User-friendly error messages

## 📈 **Business Value**

### **Use Cases**
- **📰 News Aggregation**: Stay updated with categorized news
- **🎓 Research Assistant**: AI-powered information retrieval
- **💼 Business Intelligence**: Market trends and analysis
- **🎯 Content Discovery**: Relevant information finding

### **Target Audience**
- **Professionals**: Quick news and information access
- **Researchers**: Academic and business research
- **Students**: Learning and information gathering
- **Developers**: API integration examples

## 🤝 **Contributing**

This project demonstrates advanced AI application development with enterprise-ready features. The codebase showcases:

- **Clean Architecture**: Separation of concerns and modularity
- **Best Practices**: Error handling, logging, and documentation
- **Scalable Design**: Easy to extend and maintain
- **Production Ready**: SSL handling, fallbacks, and monitoring

## 📞 **Contact & Professional Profile**

**LinkedIn**: https://www.linkedin.com/in/rajiv-c-466220321/
**Email**: rajcv92@gmail.com
**GitHub**: https://github.com/RajivC92/Agentic-AI

---

### **🔧 Technical Skills Demonstrated**

- **AI/ML Integration**: LangChain, OpenAI, NLP
- **Backend Development**: Python, API integration, databases
- **Frontend Development**: Streamlit, responsive design
- **DevOps**: Environment management, deployment
- **Architecture Design**: Microservices, workflow orchestration
- **Data Management**: SQLite, session handling
- **Error Handling**: Robust production-ready code

**Built with ❤️ and advanced AI technologies**