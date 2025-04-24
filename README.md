# MVP-Project-X




#  Gemini-Powered Medical Diagnostic Assistant

This project is a conversational AI assistant that guides users through a structured medical diagnostic interview using Google's Gemini API. It asks follow-up questions, classifies symptom categories, and produces both patient- and doctor-level reports. Conversations are stored via an external API.


##  Project Structure

 **`prototype1.py`**: Core logic for conversation flow, classification, Gemini prompts, and external record/report management.
 **`app.py`**: Flask API that wraps the diagnostic logic for external clients or UI integration.
  **`MVP-v3`**: Technical documentation followed with a release note.



##  Features

-  Uses **Gemini 1.5 Flash** for language understanding and response generation
-  Dynamically selects unused follow-up questions based on symptom category
-  Classifies symptoms into:
  - `Heart_failure`
  - `Tuberculosis`
  - `General_consultation`
- Generates:
  - **Doctor Report** (detailed, structured diagnosis)
  - **Patient Report** (simplified explanation and next steps)
-  Saves and fetches conversation history and reports via a RESTful API



##  How It Works

1. **User provides initial symptoms**
2. **Gemini classifies symptom category**
3. **Follow-up questions** are selected and asked
4. **After enough questions**, a **final diagnosis** is generated
5. **Doctor and patient reports** are created and saved



## 🔧 Setup

### 1. Install dependencies

```bash
pip install flask python-dotenv requests
```

### 2. Set environment variables

Create a `.env` file:

```env
API_KEY=your_gemini_api_key
X_API_KEY=your_internal_flask_api_key
```

### 3. Add `all questions.json`

Place the `all questions.json` file in the same directory. It should contain category-specific structured questions.



##  Running the Console Chat

```bash
python prototype1.py
```

You’ll be prompted to enter:
- Symptoms
- Authorization token
- User ID

The assistant will ask up to 15 questions and give a final diagnosis.



##  Running the Flask API

```bash
python app.py
```

Then send POST requests to:

```
POST /ai_conversation
Headers:
  x-api-key: <your_key>
  authorization: <auth_token>
  user-id: <user_id>

Body:
{
  "conversation_id": "<optional>",
  "user_response": "Fever and fatigue",
  "question": "What symptoms are you experiencing?"
}
```

Response will include:
- `flag`: `"question"` or `"diagnosis_complete"`
- `Q`: next question
- `D`: diagnosis (if complete)
- `patient_report`: simplified result
- `conversation_logs`: full Q&A history

---

## 🗃 External API Integration

This project integrates with an AWS-hosted REST API to:
- Fetch and update conversation history
- Save doctor and patient reports

Make sure the following headers are included:
- `x-tenant-id: SELF`
- `x-op: get-conversation` or `create-conversation`

---

##  Sample Output

```json
{
  "Whom to approach": "Cardiologist",
  "Differential diagnosis": "Heart failure, hypertension",
  "Suggestion": "Consult a specialist and schedule an ECG"
}
```



##  Reports

- Doctor Report: Detailed, structured, medical diagnosis
- Patient Report: Layman summary, next steps (no technical/medical terms)





