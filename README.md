# 💼 Finance App - LLM Processor

## 📦 A sophisticated personal finance management platform with intelligent transaction processing

This is a Python-based microservice that provides intelligent transaction categorization and processing using OpenAI's GPT-4. It receives transaction data via REST API, processes it through AI models, and publishes the results back to the message queue for consumption by the main finance application. The service also able to call MCP endpoint allowing you to use backend tools via **LangChain**. This enables advanced financial operations, such as transaction group analysis and custom tool execution, directly from LLM-powered workflows.

## 🎯 Current Features

✅ **AI Transaction Matching** 
  - Uses GPT-4 to categorize bank transactions into appropriate groups

✅ **Async Message Processing** 
  - RabbitMQ integration with aio_pika for reliable message handling  

✅ **Token-based Authentication**
  - Secure API access with Bearer token validation

✅ **Background Task Processing**
  - Non-blocking AI processing with FastAPI background tasks  

✅ **Robust Error Handling** 
  - Retry mechanisms and connection resilience

## 🔮 Upcoming Features

For detailed upcoming features and development progress, please check our [GitHub Issues](https://github.com/Sziszka90/FinanceApp.LLMProcessor/issues).

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

## 💻 Tech Stack

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

## 🔧 API Endpoints

```http
POST /llmprocessor/match-transactions    # Process transaction categorization (requires Bearer token)
POST /llmprocessor/prompt                # Synchronous prompt processing (requires Bearer token)
POST /wakeup                             # Wakeup endpoint
```

## 🚀 Deployment

### **Azure Container Apps**

The application is deployed as **containerized microservices** on **Azure Container Apps** using GitHub Actions.

**Deployment Flow:**

1. **Push to main** → Triggers GitHub Actions workflow
2. **Bundle** → Creates production build
3. **Deploy** → Updates hosting platform with new version
4. **Verify** → Automated health checks ensure successful deployment

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
