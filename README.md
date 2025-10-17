# **🚀 Benifix AI Agent Hackathon: Building a Smart Benefits Assistant**

## **Theme: AI Agent Tooling and Workflow**

Welcome to the Benifix Hackathon\! Your challenge is to transform a basic benefits assistant into a powerful, intelligent agent capable of advanced data retrieval, complex analysis, and system interaction using the Google Agent Development Kit (ADK) and the Gemini model.

The goal is to master **Tool Creation**, **Tool Chaining**, and **Prompt Engineering** to solve real-world employee benefits problems.

## **🛠️ Core Tooling and Setup**

The provided codebase already includes the following environment:

| Component | Description | Status |
| :---- | :---- | :---- |
| **Backend** | Flask API (simulating various services) | Running (Localhost) |
| **Database** | AlloyDB (simulated with dbsetup.sql) | Pre-configured |
| **Agent** | agent.py (The main agent runner) | Ready |
| **Toolbox** | tools.yaml (MCP Tool Definitions) | **INCOMPLETE (Requires your code)** |
| **Proxy** | places\_proxy.py (External Places API) | Complete |

### **Setup Instructions**

1. **Start the Backend:** Ensure your backend services (Flask API, Places Proxy) are running on their configured ports.  
2. **Start the MCP Toolbox:**  
   ./toolbox \--tools-file tools.yaml

3. **Run the Agent:**  
   python agent.py

## **🎯 The Challenges** 

Each challenge requires you to fill the missing code in tools.yaml (for SQL tools) or agent.py (for workflow/tool-chaining logic).

### **Challenge 1: Foundational Tools**

**Goal:** Complete the basic data retrieval capabilities that query the AlloyDB database.

| Task | File | Description |
| :---- | :---- | :---- |
| **1.1 Find Providers** | tools.yaml | Write the SQL statement for the find-providers tool to select the provider's name, specialty, location, and network status, filtering only for **IN\_NETWORK** providers based on the $1 specialty parameter. |
| **1.2 Get Employee Benefits** | tools.yaml | Write the SQL statement for the get-employee-benefits tool to retrieve the full benefits row (plan name, deductible, OOP max, HSA eligibility) for a specific $1 employee ID. |
| **1.3 Testing** | agent.py | Run a single query that successfully uses **both** tools (e.g., "My ID is 123\. What's my deductible, and can you find me a dentist?"). |

### **Challenge 2: Advanced Data Handling** 

**Goal:** Create a tool that simulates semantic search over policy documents, a key component of a Retrieval-Augmented Generation (RAG) system.

| Task | File | Description |
| :---- | :---- | :---- |
| **2.1 Semantic Policy Search** | tools.yaml | Write the SQL statement for the search-policy-documents tool. This tool needs to search the document\_chunks table, filtering the content column for the $1 query\_text using a LIKE operator, and limiting the results to the $2 max\_results parameter. |
| **2.2 RAG Integration (Conceptual)** | agent.py | Ensure your agent's system prompt (agent.py) guides the Gemini model to use the retrieved chunks from this tool to synthesize a final, grounded answer to the user's complex policy question (e.g., "Does my Gold PPO plan cover fertility treatments?"). |

### **Challenge 3: Numerical & Predictive Analysis**

**Goal:** Implement the data retrieval necessary for the agent to perform a complex, chained numerical calculation (cost prediction).

| Task | File | Description |
| :---- | :---- | :---- |
| **3.1 Plan Details Retrieval** | tools.yaml | Write the SQL statement for the get-employee-plan-details tool, retrieving the deductible and OOP max for an employee ID. |
| **3.2 Usage Profile Retrieval** | tools.yaml | Write the SQL statement for the get-usage-profile-assumptions tool, retrieving the claims and visit assumptions for a specific $1 usage profile (low, average, high). |
| **3.3 Agent Workflow** | agent.py | The agent must correctly chain these two tools, retrieve the data, and then perform the calculation (either in a Python tool or relying on the Gemini model's reasoning based on the retrieved data) to predict the cost. *(The calculation logic itself is complex, making this the highest challenge)*. |

### **Challenge 4: Places API Integration (External Tool Chaining)**

**Goal:** Integrate a powerful external HTTP tool (find-closest-provider-by-address) with the internal SQL tools to find the closest in-network provider, requiring complex multi-step reasoning.

#### **AI Key Setup** 

The places\_proxy.py file requires a **Google Maps API Key**. For this challenge, you must: 

1. **Generate a Key:** Get a new API key from Google Cloud Console.   
2. **Enable Service:** Ensure the **Places API** and **Geocoding API** services are enabled in your project.   
3. **Restrict the Key:**   
   1. **Application Restrictions:** Restrict the key to the specific IP address where your places\_proxy.py service is running.   
   2. **API Restrictions:** Restrict the key to only use the **Places API** and **Geocoding API**   
4. **Update:** Replace the placeholder **\<Maps\_API\_KEY\>** in the places\_proxy.py with the secured key. 

| Task | File | Description |
| :---- | :---- | :---- |
| **5.1 Provider Location DB Search** | tools.yaml | Write the SQL statement for the get-provider-locations tool. This is similar to 1.1 but must also include an optional location filter ($2). |
| **5.2 Agent Chaining Logic** | agent.py | **(Mental Challenge)** The team must update the agent's prompt to correctly specify the complex chaining logic: **FIRST** call get-provider-locations (SQL) to find in-network providers, **THEN** call find-closest-provider-by-address (HTTP Proxy) to find nearby places, and **FINALLY** cross-reference the two result sets to recommend a provider that is *both* in-network and close. |

### **Challenge 6: Custom Web UI with Firebase Studio**

**Goal:** Build a functional, single-page chat client that can send queries to the fully-built AI agent, showcasing the entire solution in a user-friendly interface.

**Context:** The assumption for this challenge is that the completed Python agent (agent.py) has been deployed as an accessible **HTTP endpoint** (e.g., via Cloud Run or Cloud Functions) that accepts chat messages and returns responses.

| Task | File | Description |
| :---- | :---- | :---- |
| **6.1 UI Design & Setup** | *New HTML File* | Create a visually appealing, responsive single-page chat application using **HTML, Tailwind CSS, and JavaScript**. The interface must have an input field and a display area for conversation history. |
| **6.2 Chat Logic** | *New HTML File* | Implement JavaScript logic to send the user's query and a **Session ID** as a structured JSON object to a mock API endpoint (`/agent/chat`) and parse the agent's JSON response, ensuring **multi-turn history** is maintained in the UI.. |
| **6.3 Agent Integration (Conceptual)** | *New HTML File* | Demonstrate the integration by having the chat client send and receive structured JSON data, proving that the front-end is ready to connect to the deployed Gemini/ADK service. |

Good luck, Benifix Hackathon participants\! May the tools be ever in your favor.