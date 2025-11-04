# Compose for Agents Demos

Этот репозиторий содержит коллекцию примеров использования **Docker Compose** для оркестрации различных фреймворков и инструментов для создания AI-агентов.

## 🚀 Улучшения в этом Pull Request

*   **Улучшена структура проекта:** Обновлен файл `.gitignore` для лучшей совместимости и исключения служебных файлов.
*   **Актуализация документации:** Обновлены инструкции в `README.md`.

## 🛠 Предварительные требования

+ **[Docker Desktop] 4.43.0+ или [Docker Engine]** установлен.
+ **A laptop or workstation with a GPU** (e.g., a MacBook) для запуска локальных моделей. Если у вас нет GPU, вы можете использовать **[Docker Offload]**.
+ Если вы используете [Docker Engine] на Linux или [Docker Desktop] на Windows, убедитесь, что [Docker Model Runner requirements] выполнены (в частности, включена поддержка GPU) и установлены необходимые драйверы.
+ Если вы используете Docker Engine на Linux, убедитесь, что у вас установлен [Docker Compose] 2.38.1 или более поздней версии.

## ⚙️ Запуск Демонстраций

Каждая демонстрация является самодостаточной и может быть запущена локально или с использованием облачного контекста. Запуск состоит из трех шагов:

1.  Перейдите в корневую директорию проекта (например, `./a2a`).
2.  Создайте файл `.mcp.env` из примера `mcp.env.example` (если он существует) и укажите необходимые токены MCP.
3.  Запустите `docker compose up --build`.

### Использование моделей OpenAI

Демонстрации поддерживают использование моделей OpenAI вместо локального запуска моделей с помощью Docker Model Runner. Для использования OpenAI:

1.  Создайте файл `secret.openai-api-key` с вашим ключом OpenAI API:
    ```plaintext
    sk-...
    ```
2.  Запустите проект с конфигурацией OpenAI:
    ```sh
    docker compose -f compose.yaml -f compose.openai.yaml up
    ```

## 📚 Демонстрации

| Demo | Agent System | Models | MCPs | project | compose |
| :--- | :--- | :--- | :--- | :--- | :--- |
| [A2A](https://github.com/a2a-agents/agent2agent) Multi-Agent Fact Checker | Multi-Agent | OpenAI | duckduckgo | [./a2a](./a2a) | [compose.yaml](./a2a/compose.yaml) |
| [Agno](https://github.com/agno-agi/agno) agent that summarizes GitHub issues | Multi-Agent | qwen3(local) | github-official | [./agno](./agno) | [compose.yaml](./agno/compose.yaml) |
| [Vercel AI-SDK](https://github.com/vercel/ai) Chat-UI for mixing MCPs and Model | Single Agent | llama3.2(local), qwen3(local) | wikipedia-mcp, brave, resend(email) | [./vercel](./vercel) | [compose.yaml](https://github.com/slimslenderslacks/scira-mcp-chat/blob/main/compose.yaml) |
| [CrewAI](https://github.com/crewAIInc/crewAI) Marketing Strategy Agent | Multi-Agent | qwen3(local) | duckduckgo | [./crew-ai](./crew-ai) | [compose.yaml](https://github.com/docker/compose-agents-demo/blob/main/crew-ai/compose.yaml) |
| [ADK](https://github.com/google/adk-python) Multi-Agent Fact Checker | Multi-Agent | gemma3-qat(local) | duckduckgo | [./adk](./adk) | [compose.yaml](./adk/compose.yaml) |
| [ADK](https://github.com/google/adk-python) & [Cerebras](https://www.cerebras.ai/) Golang Experts | Multi-Agent | unsloth/qwen3-gguf:4B-UD-Q4_K_XL & ai/qwen2.5:latest (DMR local), llama-4-scout-17b-16e-instruct (Cerebras remote) |  | [./adk-cerebras](./adk-cerebras) | [compose.yml](./adk-cerebras/compose.yml) |
| [LangGraph](https://github.com/langchain-ai/langgraph) SQL Agent | Single Agent | qwen3(local) | postgres | [./langgraph](./langgraph) | [compose.yaml](./langgraph/compose.yaml) |
| [Embabel](https://github.com/embabel/embabel-agent) Travel Agent | Multi-Agent | qwen3, Claude3.7, llama3.2, jimclark106/all-minilm:23M-F16 | brave, github-official, wikipedia-mcp, weather, google-maps, airbnb | [./embabel](./embabel) | [compose.yaml](https://github.com/embabel/travel-planner-agent/blob/main/compose.yaml) and [compose.dmr.yaml](https://github.com/embabel/travel-planner-agent/blob/main/compose.dmr.yaml) |
| [Spring AI](https://spring.io/projects/spring-ai) Brave Search | Single Agent | none | duckduckgo | [./spring-ai](./spring-ai) | [compose.yaml](./spring-ai/compose.yaml) |
| [ADK](https://github.com/google/adk-python) Sock Store Agent | Multi-Agent | qwen3 | MongoDb, Brave, Curl,  | [./adk-sock-shop](./adk-sock-shop/) | [compose.yaml](./adk-sock-shop/compose.yaml) |
| [Langchaingo](https://github.com/tmc/langchaingo) DuckDuckGo Search | Single Agent | gemma3 | duckduckgo | [./langchaingo](./langchaingo) | [compose.yaml](./langchaingo/compose.yaml) |
| [MinionS](https://github.com/HazyResearch/minions) Cost-Efficient Local-Remote Collaboration | Local-Remote Protocol | qwen3(local), gpt-4o(remote) |  | [./minions](./minions) | [docker-compose.minions.yml](https://github.com/HazyResearch/minions/blob/main/apps/minions-docker/docker-compose.minions.yml) |

## 📜 Лицензия

Этот репозиторий имеет **двойную лицензию** (Apache License 2.0 или MIT License). Вы можете выбрать любую из них для использования вклада, сделанного Docker в этом репозитории.

> ℹ️ **Примечание:** Каждый пример может иметь свой собственный файл `LICENSE`. Они предоставляются для отражения любых сторонних лицензионных требований, которые применяются к этому конкретному примеру, и их необходимо соблюдать.

`SPDX-License-Identifier: Apache-2.0 OR MIT`

[Docker Compose]: https://github.com/docker/compose
[Docker Desktop]: https://www.docker.com/products/docker-desktop/
[Docker Engine]: https://docs.docker.com/engine/
[Docker Model Runner requirements]: https://docs.docker.com/ai/model-runner/
[Docker Offload]: https://www.docker.com/products/docker-offload/
