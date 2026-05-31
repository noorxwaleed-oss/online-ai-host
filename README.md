# 🎙️ Online AI-host

[![WEBSITE](https://img.shields.io/badge/WEBSITE-gray?style=for-the-badge&logo=supabase&logoColor=white)](https://www.webpagetest.org/blank.html)
  <img src='https://img.shields.io/badge/RESEARCH-blue?style=for-the-badge'>
</a>
</a>
<a href='https://www.webpagetest.org/blank.html'>
  <img src='https://img.shields.io/badge/FEEDBACK-orange?style=for-the-badge'>
</a>
</br>
## ✨ Overview 
It is an innovative multi-agent platform that transforms raw inputs—such as text, videos, or files—into high-quality, professional interview products. By leveraging advanced AI, the system generates dynamic scripts, enables users to create a customized host persona and automates post-production tasks like social media clipping and cover art design . It simplifies the entire process of turning static content into ready-to-publish podcasts and articles.

---  

## ⚡ Key Features
- **🤖 Dynamic Scripting**: AI agents that analyze context to write natural interview scripts.
- **🎭 Customization Host Persona**: Tailor your host’s personality—from "Professional Journalist" to "Casual Tech Enthusiast."
- **⚡ Multi-Agent Logic**: Parallel processing where specialized agents handle research, scripting, and audio quality.

 ---
  ## 🏗️ System Architecture

At the core of Online AI-host is a collaborative ecosystem of specialized agents. Rather than relying on a single prompt, our system utilizes **a Multi-Agent Orchestration** flow :

1. **Input Layer**: Accepts raw text, PDF, or Video URLs.
2. **Analysis Agent (The Brain)**: Uses LLMs to extract key themes and sentiment.
3. **Persona Agent (The Soul)**: Injects specific tone and character traits into the data.
4. **Script Agent (The Writer)**: Formats the final output into a professional interview script.
5. **Output Layer**: Delivers the ready-to-publish podcast file.
---

## ⚙️ Under the Hood
**Generative AI** 
- Dynamic Scripting: Automatically drafting high-quality, professional interview scripts.
- Content Transformation: Turning raw video, text, or files into ready-to-publish articles.
- Creative Assets: Generating automated cover art and social media promotional clips.

**Agentic AI**
- Host Persona Engine: Crafting autonomous agents with customized personalities and tones.
- Decision Making: Smart agents that choose the most engaging "hooks" from your raw input.

**RAG (Retrieval-Augmented Generation)**
- Custom Knowledge: The AI "studies" your specific files and videos to learn the facts.
- Fact-Checking: It stays 100% loyal to your data so it never makes things up.
- Deep Search: It finds the best "gold nuggets" hidden inside your long videos or documents.

**Memory System**
- Conversation Flow: It remembers what was said earlier so the interview feels natural.
- Persona Memory: It saves your host’s unique style and voice to use in later projects.

---

## 🧱 Tech Stack
**Intelligence & Logic**
- Python.
- OpenAI GPT Models / LLMs
- Hugging Face Models.
- LangGraph / AutoGen

**Frontend & Interface**
- HTML/CSS

**Backend & Storage**
- FastAPI
---
## 📂 Project Structure
```c
online-ai-host/
│
├── agents/                 
│   ├── host_agent.py       
│   ├── researcher_agent.py  
│   ├── script_writer.py    
│   └── post_producer.py    
│
├── rag/                     
│   ├── raw_inputs/         
│   ├── vector_store.py     
│   └── retriever.py        
│
├── memory/                  
│   ├── short_term.py        
│   └── persona_history.py   
│
├── api/                     
│   └── main.py              
│
├── frontend/                
│   ├── index.html           
│   └── style.css            
│
├── assets/                 
│   ├── generated_scripts/
│   └── cover_art/
│
├── requirements.txt        
└── README.md             
```
---

## 📊 Evaluation (Quality Control)
We don't just generate text; we ensure quality. We evaluate our system by asking three critical questions:
- Does the script stick only to the facts in the uploaded files?
- Does the AI-Host ask meaningful questions related to the topic?
- Does our retriever find the most important "gold nuggets" from the source?

---
## 📽️ Demo
---
## ⚖️ License 
This project is developed as part of the **DEPI (Digital Egypt Pioneers Initiative)** Graduation Project.

* **Track:** AI & Data Science.
* **Course:** Generative & Agentic AI
* **Project Type:** Final Graduation Submission
* **Date:** 2026

---
## 👥 team members
