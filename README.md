# 🤖 LLM Processor Service

📦 **AI-powered transaction categorization microservice for Personal Finance App**

This is a Python-based microservice that provides intelligent transaction categorization using OpenAI's GPT-4. It receives transaction data via REST API, processes it through AI models, and publishes the results back to the message queue for consumption by the main finance application.

🧠 **LangGraph Agent Orchestration** - The service uses LangGraph as the agent framework to orchestrate LLM-powered workflows, enabling advanced tool usage, structured output, and multi-step reasoning for financial queries.

### 🎯 Core Features

✅ **AI Transaction Matching** - Uses GPT-4 to categorize bank transactions into appropriate groups  
✅ **FastAPI Framework** - Modern, fast web framework with automatic API documentation  
✅ **Async Message Processing** - RabbitMQ integration with aio_pika for reliable message handling  
✅ **Token-based Authentication** - Secure API access with Bearer token validation  
✅ **Background Task Processing** - Non-blocking AI processing with FastAPI background tasks  
✅ **Robust Error Handling** - Retry mechanisms and connection resilience

## 🏗️ Architecture

### **Service Structure**

```
main.py                                 # FastAPI application and endpoints
requirements.txt                        # Python dependencies
LLMProcessor.Dockerfile                 # Docker setup
rabbitmq_config.json                    # Message queue configuration

📁 clients/                             # API and messaging clients
  McpClient.py                          # MCP API client
  RabbitMqClient.py                     # RabbitMQ client
  📁 abstraction/                       # Client interfaces

📁 services/                            # Business logic and orchestration
  LLMService.py                         # LangGraph agent orchestration
  PromptService.py                      # Prompt generation logic
  LoggerService.py                      # Logging
  TokenService.py                       # Token validation
  📁 abstraction/                       # Service interfaces

📁 models/                              # Pydantic request/response models
  MatchTransactionRequest.py            # Request model
  MatchTransactionResponse.py           # Response model
  McpEnvelope.py                        # Envelope model
  McpRequest.py                         # MCP request model
  McpTopTransactionGroupsRequest.py     # Top transaction groups request
  Message.py                            # Generic message model
  ChatMessage.py                        # Chat message model
  PromptRequest.py                      # Prompt request model

📁 tools/                               # Tool definitions and factories for LangGraph
  ToolFactory.py                        # Tool factory
  McpTool.py                            # MCP tool
  📁 abstraction/                       # Tool interfaces

📁 di/                                  # Dependency injection setup
  AppModule.py                          # DI module
  dependencies.py                       # DI dependencies

📁 dependencies/                        # Global exception handler
  global_exception_handler.py           # Exception handler

📁 utils/                               # Utility functions
  camelcase.py                          # CamelCase converter

📁 .github/workflows/                   # CI/CD pipeline
  deploy.yaml                           # Deployment workflow
```

### **Key Patterns**

- **Microservice Architecture** - Focused, single-responsibility service
- **Async/Await** - Non-blocking operations throughout
- **Message-Driven Architecture** - RabbitMQ for reliable communication
- **Background Processing** - FastAPI background tasks for AI processing
- **Retry Patterns** - Robust error handling with exponential backoff

## 🚀 Tech Stack

### **Python Framework & Libraries**

- **FastAPI** - Modern, fast web framework with automatic OpenAPI documentation
- **Uvicorn** - Lightning-fast ASGI server for production deployment
- **Pydantic** - Data validation and settings management using Python type annotations
- **LangGraph** - Agent orchestration framework for LLM-powered workflows
- **LangChain** - LLM orchestration, prompt engineering, and tool integration
- **OpenAI** - Official Python client for GPT-4 integration
- **aio_pika** - Async RabbitMQ client for reliable message processing
- **httpx** - Modern async HTTP client for external API calls

### **AI & Machine Learning**

- **OpenAI GPT-4** - Advanced language model for intelligent transaction categorization
- **Prompt Engineering** - Optimized prompts for financial transaction analysis
- **Async Processing** - Non-blocking AI inference for high throughput
- **Async Processing** - Non-blocking AI inference for high throughput

### **Message Queuing & Communication**

- **RabbitMQ** - Reliable message broker with persistent queues
- **aio_pika** - Async Python client for RabbitMQ integration
- **Exchange-based routing** - Flexible message routing with exchanges and bindings
- **Retry mechanisms** - Robust error handling with exponential backoff

### **Infrastructure & Security**

- **Bearer Token Authentication** - Secure API access control
- **Environment Configuration** - Secure credential management
- **Health Monitoring** - Connection health checks and automatic recovery
- **Docker Support** - Containerized deployment ready

## 🔧 API Endpoints

### **Transaction Matching**

```http
POST /llmprocessor/match-transactions    # Process transaction categorization (requires Bearer token)
POST /llmprocessor/prompt                # Synchronous prompt processing (requires Bearer token)
POST /wakeup                             # Wakeup endpoint
```

### **Environment Configuration**

Create a `.env` file or set environment variables:

```bash
# OpenAI Configuration
LLM_API_KEY=your-openai-api-key

# API Security
API_TOKEN=your-secret-api-token

# MCP endpoint
MCP_API_BASE_URL=your-mcp-endpoint

# RabbitMQ Configuration
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASS=guest
```

### **RabbitMQ Configuration**

The service requires RabbitMQ with specific exchanges and queues defined in `rabbitmq_config.json`:

```json
{
  "RabbitMqSettings": {
    "Exchanges": [
      {
        "ExchangeName": "transactions.exchange",
        "ExchangeType": "direct"
      }
    ],
    "Queues": ["transactions.matched"],
    "Bindings": [
      {
        "Exchange": "transactions.exchange",
        "Queue": "transactions.matched",
        "RoutingKey": "transactions.matched"
      }
    ],
    "RoutingKeys": {
      "TransactionsMatched": {
        "RoutingKey": "transactions.matched",
        "ExchangeName": "transactions.exchange"
      }
    }
  }
}
```

### **Running the Service**

```bash
# Start the FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# The API will be available at:
# http://localhost:8000
# API Documentation: http://localhost:8000/docs
```

## 🐳 Docker Deployment

### **Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Docker Compose**

```yaml
version: "3.8"
services:
  llm-processor:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LLM_API_KEY=${LLM_API_KEY}
      - API_TOKEN=${API_TOKEN}
      - RABBITMQ_HOST=rabbitmq
    depends_on:
      - rabbitmq

  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/ai-improvement`)
3. Commit your changes (`git commit -m 'Improve AI categorization accuracy'`)
4. Push to the branch (`git push origin feature/ai-improvement`)
5. Open a Pull Request

## 🔗 Related Projects

- **[FinanceApp.Backend](https://github.com/Sziszka90/FinanceApp.Backend)** - Main .NET backend service
- **[FinanceApp.Frontend](https://github.com/Sziszka90/FinanceApp.Frontend)** - Angular frontend application

## 👤 Author

**Szilard Ferencz**  
🌐 [szilardferencz.dev](https://www.szilardferencz.dev)  
💼 [LinkedIn](https://www.linkedin.com/in/szilard-ferencz/)  
🐙 [GitHub](https://github.com/Sziszka90)

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

⭐ **Star this repo if you find it helpful!** ⭐
