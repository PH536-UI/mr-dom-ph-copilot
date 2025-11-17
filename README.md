# Mr. DOM PH Copilot – IA distribuída para CRM e mensageria

Um sistema de IA modular e distribuído, orquestrado com LangChain, LangGraph e Agno, integrado ao ecossistema de automação N8N, CRM (Vtiger), marketing (Mautic), mensageria (Chatwoot, Evolution API) e visualização (Power BI). O objetivo é demonstrar domínio técnico e protagonismo em soluções reais de IA corporativa.

## 🧠 Visão Geral do Projeto

Este projeto visa demonstrar expertise na aplicação de **Inteligência Artificial** em cenários corporativos, focando em **CRM, mensageria e automação distribuída**.

## 🛠️ Stack Tecnológica

| Camada | Ferramenta | Finalidade |
|---|---|---|
| IA Cognitiva | LangChain + LangGraph + Agno | Orquestração de agentes inteligentes |
| Backend | Python + FastAPI | APIs RESTful e microserviços |
| Automação | N8N | Webhooks, fluxos e integrações |
| CRM | Vtiger | Gestão de clientes e leads |
| Marketing | Mautic | Campanhas e segmentação |
| Mensageria | Chatwoot + Evolution API | Atendimento multicanal |
| Visualização | Power BI | Dashboards e insights |
| DevOps | GitHub Actions + Docker | CI/CD e deploy automatizado |

## 🔁 Fluxo de Integração

1. **Usuário interage via mensageria (WhatsApp, Telegram, etc.)**
2. **Chatwoot/Evolution API → N8N → LangChain Agent**
3. **LangChain consulta CRM (Vtiger), campanhas (Mautic), histórico**
4. **Resposta contextualizada é enviada ao usuário**
5. **Logs e métricas são enviados ao Power BI**

## 📂 Estrutura do Repositório

- `/agents`: agentes LangChain/LangGraph
- `/api`: FastAPI endpoints
- `/n8n-flows`: exportações dos fluxos N8N
- `/integrations`: conectores para Vtiger, Mautic, Chatwoot
- `/docs`: documentação técnica e planos de projeto
- `/ci-cd`: pipelines GitHub Actions

## 🧪 Provas de Proficiência

Este projeto servirá como prova de proficiência nas seguintes áreas:

- **Python:** agentes com LangChain + integração RESTful com FastAPI
- **LangChain/LangGraph:** chains, tools, memory, embeddings, agents
- **N8N:** fluxos com webhooks, chamadas REST, triggers e automações
- **Agno Framework:** orquestração de agentes distribuídos
- **Mensageria:** integração com Chatwoot e Evolution API via N8N
- **CI/CD:** deploy automatizado com GitHub Actions e Docker

---

*Este README foi gerado com base no plano de projeto fornecido em `docs/project_plan.md`.*
