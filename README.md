# QUANTUM-ARC Customer Support Chatbot

**Quantum Arc** is an intelligent, human-like customer support chatbot designed for premium electronics retailers. Python version used is `3.13`. It uses the powerful `deepseek/deepseek-r1-0528:free` model via OpenRouter API to answer customer queries with high accuracy and professionalism. The chatbot handles FAQs, product specs, and store policies — and even escalates unresolved queries to human support intelligently.

---

> 💡 Without Setup, this code will not work. Follow the Setup below to make this code working.

---

## 🚀 Features

- 🔍 **Strictly Context-Based Answers**  
  Responds *only* using internal company data — no hallucinations or guessing.

- 🤖 **LLM-Powered, Human-Like Interaction**  
  Uses OpenRouter’s `deepseek-r1-0528:free` for clear and short answers with conversational tone.

- 📩 **Email Fallback & Logging System**  
  If an answer is not found, it:
  - Requests the user's email
  - Extracts both the email and clarified question intelligently
  - Logs them with timestamp in `unanswered_queries.jsonl` for human follow-up

- 🛒 **Tailored for Tech Retail**  
  Specializes in smartphones, laptops, desktops, and accessories — with support for both policy and product queries.

- 🖥️ **GUI for End Users**  
  A desktop app (`QUANTUM ARC.exe`) is included in the `Website Application` folder for easy distribution to customers.

---

## 🧪 Getting Started (Source Code)

Follow these steps to set up and run the chatbot locally.

### 1. Get OpenRouter API Key

- Sign up at [https://openrouter.ai](https://openrouter.ai)
- Go to **[Integrations](https://openrouter.ai/settings/integrations)** and generate your API key

### 2. Create `.env` File

Create a `.env` file inside the `Assets/` folder:

```
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=deepseek/deepseek-r1-0528:free
```

### 3. Set Up Virtual Environment (Recommended)

Create the virtual environment:
```
python -m venv VirtualEnvironment
```
Activate the environment:
```
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
.\VirtualEnvironment\Scripts\Activate.ps1
```

### 4. Install Requirements

```
pip install -r requirements.txt
```

### 5. Paths Correction

1. In any of the files where you see the paths, **Remove** `Source Code/` from there.
for example,
From:
```
Source Code/Assets/logo.png
```
To:
```
Assets/logo.png
```

2. In the API and Model calling in `llm_interface.py`
Replace:
```
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
OPENROUTER_MODEL = st.secrets["OPENROUTER_MODEL"]
```
To this:
```
load_dotenv("Assets/.env")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL")
```

### 6. Prepare Your Data

Edit these files inside `Assets/` according to your store info:

- `faqs.json`

- `products.json`

- `policies.json`

Maintain the same format.

### 7. Preprocess the Data

```
python preprocess_chunks.py
```
✅ This generates `chunks.json`.

### 8. Embed the Chunks

```
python embed_chunks.py
```
✅ This generates `embedded_chunks.pkl`.

### 9. Run the Chatbot

Option 1
```
streamlit run main.py
```
Option 2
```
python launcher.py
```

---

## 📁 Project Structure

```
QUANTUM ARC - Customer Support Chatbot
│
├── Source Code
│   ├── __pycache__/
│   │
│   ├── Assets/
│   │   ├── .env                           (Make the .env file and put the secrets here)
│   │   ├── chunks.json
│   │   ├── embedded_chunks.pkl
│   │   ├── faqs.json
│   │   ├── icon.ico
│   │   ├── logo.png
│   │   ├── policies.json
│   │   ├── products.json
│   │   └── unanswered_queries.jsonl
│   │
│   ├── VirtualEnvironment/                (You have to make your own virtual environment)
│   │
│   ├── embed_chunks.py
│   ├── embed_query.py
│   ├── launcher.py
│   ├── llm_interface.py
│   ├── main.py
│   ├── preprocess_chunks.py
│   ├── ProgramEngine.py
│   ├── prompt_builder.py
│   └── similarity.py
│
├── Website Application
│   └── QUANTUM ARC.exe                    (This is the application)
│
├── LICENSE
├── README.md                              (You are here)
└── requirements.txt
```

---

## 👨‍💻 Creator

Developed by **Muhammad Ali Musawir**
📧 `muhammadalimusawir@gmail.com`

---

## ⚖️ License
This project is licensed under the **Apache 2.0 License** — free to use, modify, and distribute with proper credit.

---

> 💡 Need help? Have a question or idea? Feel free to reach out via email!

Let me know if you'd also like a badge header (e.g. Python version, license, model used) or a GIF/image preview section — I can add that too!

