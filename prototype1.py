# import os
# import json
# import uuid
# import requests

# # Load API key
# API_KEY = os.getenv("API_KEY")
# GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

# # Load the questions
# with open("all questions.json", "r", encoding="utf-8") as f:
#     QUESTION_DATA = json.load(f)

# conversation_history = []

# # ------------------- External Storage Functions -------------------
# def get_record(conversation_id, authorization):
#     url = f"https://wogrli5cm6.execute-api.ap-south-1.amazonaws.com/api-patient-otp-dev/conversation/{conversation_id}"
#     headers = {
#         'x-tenant-id': 'SELF',
#         'Authorization': authorization,
#         'x-op': 'get-conversation'
#     }
#     response = requests.get(url, headers=headers)
#     print("record response ", response.text)
#     return response.json()

# def create_record(conversation_id, user_id, question, answer, authorization):
#     url = "https://wogrli5cm6.execute-api.ap-south-1.amazonaws.com/api-patient-otp-dev/conversation"
#     payload = json.dumps({
#         "conversation_id": conversation_id,
#         "conversation_type": "gemini",
#         "user_id": user_id,
#         "conversation": [{"question": question, "answer": answer, "message": ""}],
#         "file_uploads": []
#     })
#     headers = {
#         'x-tenant-id': 'SELF',
#         'Authorization': authorization,
#         'x-op': 'create-conversation',
#         'Content-Type': 'application/json'
#     }
#     response = requests.post(url, headers=headers, data=payload)
#     return response.json()

# # ------------------- Gemini & Question Logic -------------------

# def query_gemini(prompt):
#     payload = {"contents": [{"parts": [{"text": prompt}]}]}
#     headers = {"Content-Type": "application/json"}

#     try:
#         response = requests.post(GEMINI_API_URL, json=payload, headers=headers, timeout=10)
#         print("response", response.json())  # Keep for debugging
#         gemini_response = response.json()

#         if "candidates" in gemini_response:
#             text = gemini_response["candidates"][0]["content"]["parts"][0]["text"].strip()

#             # For classification responses that are expected to be plain text
#             if prompt.startswith("Classify the following symptoms"):
#                 return text.strip()
            
#             # If we're expecting a question but got plain text without JSON formatting
#             if "Ask ONE best follow-up question" in prompt and not (text.startswith("{") or text.startswith("```")):
#                 # Convert plain text question to JSON format
#                 return {
#                     "question": text,
#                     "reason": "Auto-formatted from plain text response"
#                 }

#             # Handle JSON in code block format (```json ... ```)
#             if text.startswith("```json") and text.endswith("```"):
#                 text = text.replace("```json", "").replace("```", "").strip()
            
#             # Handle raw JSON response
#             if text.startswith("{") and text.endswith("}"):
#                 try:
#                     return json.loads(text)
#                 except json.JSONDecodeError:
#                     print(" Could not parse JSON. Raw response:", text)
#                     return {"error": "Failed to parse response", "raw_text": text}
            
#             # Try to parse into JSON anyway as a fallback
#             try:
#                 return json.loads(text)
#             except json.JSONDecodeError:
#                 print(" Could not parse JSON. Raw response:", text)
#                 # Instead of failing, convert plain text to a question format
#                 if "Ask ONE best follow-up question" in prompt or "ask next question" in prompt.lower():
#                     return {
#                         "question": text,
#                         "reason": "Auto-formatted from non-JSON response"
#                     }
#                 return {"error": "Failed to parse response", "raw_text": text}

#         else:
#             print(" Gemini response malformed:", gemini_response)
#             return {"error": "Malformed response"}

#     except Exception as e:
#         print(" Gemini API error:", e)
#         return {"error": str(e)}

# def classify_category(symptom_context):
#     prompt = (
#         f"Classify the following symptoms or conversation into one of:\n"
#         f"- Heart_failure\n- Tuberculosis\n- General_consultation\n\n"
#         f"Input: {symptom_context}\n\nReturn only the category name."
#     )
#     result = query_gemini(prompt)
#     # Handle both string and dict responses
#     if isinstance(result, dict) and "raw_text" in result:
#         return result["raw_text"]
#     return result

# def get_unused_questions(category, history):
#     asked = {entry["question"].lower() for entry in history}
#     all_qs = [q["Question"] for q in QUESTION_DATA.get(category, [])]
#     return [q for q in all_qs if q.lower() not in asked]

# def ask_gemini_next_question(symptoms, history, available_questions):
#     history_text = "\n".join([f"Q: {h['question']}\nA: {h['answer']}" for h in history])
#     question_block = "\n".join(f"- {q}" for q in available_questions)
#     force_question = len(history) < 6

#     if force_question:
#         prompt = (
#             f"You are a medical AI assistant.\n\n Patient's symptoms: {symptoms}\n Conversation so far:\n{history_text}\n\n Available follow-up questions:\n{question_block}\n\n"
#             f"Ask ONE best follow-up question (avoid repetition).\n"
#             f" You MUST Respond in JSON: {{\"question\": \"...\", \"reason\": \"...\"}}"
#         )
#     else:
#         prompt = (
#             f"You are a medical AI assistant.\n\nPatient's symptoms: {symptoms}\n Conversation so far:\n{history_text}\n\n"
#             f"Available follow-up questions:\n{question_block}\n\n"
#             f"Ask ONE best question OR if enough data, return diagnosis.\n You MUST Respond in JSON"
#             f"Diagnosis format: {{\"Whom to approach\": \"...\", \"Differential diagnosis\": \"...\", \"Suggestion\": \"...\"}}"
#         )
#     return query_gemini(prompt)

# def ask_final_diagnosis(symptoms, history):
#     history_text = "\n".join([f"Q: {h['question']}\nA: {h['answer']}" for h in history])
#     prompt = (
#         f"You are a senior medical AI.\nPatient symptoms: {symptoms}\nConversation:\n{history_text}\n\n"
#         f"Give FINAL diagnosis in JSON:\n"
#         f"{{\n  \"Whom to approach\": \"...\",\n  \"Differential diagnosis\": \"...\",\n  \"Suggestion\": \"...\",\n  \"reason\": \"...\"\n}}"
#     )
#     return query_gemini(prompt)

# def create_patient_report(symptoms, history, doctor_diagnosis):
#     prompt = (
#             f"Create a simplified patient report based on these symptoms and conversation:\n"
#             f"Symptoms: {symptoms}\nConversation:\n" + "\n".join([f"Q: {h['question']}\nA: {h['answer']}" for h in history]) + "\n\n"
#             f"Create a simplified explanation of their condition . You can mention if the condition is obstructive or restrictive but nothing else. DO NOT include differential diagnoses or detailed medical terminology. Next steps should mention consulting with a doctor. No other advice. Format as a JSON with keys: 'Condition_summary', 'Next_steps'"
#     )
#     return query_gemini(prompt)

# def save_reports(symptoms, history, doctor_diagnosis, patient_report):
#     report_id = uuid.uuid4().hex[:8]
#     with open(f"doctor_report_{report_id}.json", "w") as f:
#         json.dump({"symptoms": symptoms, "conversation": history, "diagnosis": doctor_diagnosis}, f, indent=2)
#     with open(f"patient_report_{report_id}.json", "w") as f:
#         json.dump({"symptoms": symptoms, "conversation": history, "simplified_information": patient_report}, f, indent=2)

# def run_chat():
#     print("🩺 Welcome to the diagnostic assistant!")
#     symptoms = input("Describe your symptoms: ").strip()
#     authorization = input("Enter authorization token: ").strip()
#     user_id = input("Enter user ID: ").strip()

#     conversation_id = str(uuid.uuid4())
#     question_count = 0
#     max_questions = 15
#     min_questions = 6

#     # Create initial record
#     create_record(
#         conversation_id=conversation_id,
#         user_id=user_id,
#         question="🩺 Welcome to the diagnostic assistant! Describe your symptoms:",
#         answer=symptoms,
#         authorization=authorization
#     )

#     while question_count < max_questions:
#         record = get_record(conversation_id, authorization)
#         print("record", record)
#         history = record.get("conversation", [])

#         full_text = symptoms + "\n" + "\n".join(f"Q: {x['question']} A: {x['answer']}" for x in history)
#         category = classify_category(full_text)
#         available_qs = get_unused_questions(category, history)

#         response = ask_gemini_next_question(symptoms, history, available_qs)

#         if isinstance(response, dict) and 'Differential diagnosis' in response and question_count >= min_questions:
#             print(f"\n Diagnosis complete after {question_count} questions.")
#             patient_report = create_patient_report(symptoms, history, response)
#             save_reports(symptoms, history, response, patient_report)
#             print(f"\n Summary: {patient_report}")
#             return

#         if isinstance(response, dict) and "question" in response:
#             question = response["question"]
#             reason = response["reason"]
#             print(f"\nDoctor's Question ({question_count + 1}): {question}")
#             answer = input("Patient's Answer: ").strip()
#             create_record(conversation_id, user_id, question, answer, authorization)
#             question_count += 1
#         else:
#             print(" Unexpected Gemini response.")
#             break

#     print("\n Max questions reached. Final diagnosis in progress...")
#     record = get_record(conversation_id, authorization)
#     history = record.get("conversation", [])
#     final_diagnosis = ask_final_diagnosis(symptoms, history)
#     patient_report = create_patient_report(symptoms, history, final_diagnosis)
#     save_reports(symptoms, history, final_diagnosis, patient_report)
#     print(f"\n Final Diagnosis:\n{final_diagnosis}")


import os
import json
import uuid
import requests

# Load API key
API_KEY = os.getenv("API_KEY")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

# Load the questions
with open("all questions.json", "r", encoding="utf-8") as f:
    QUESTION_DATA = json.load(f)

# ------------------- External Storage Functions -------------------
# def get_record(conversation_id, authorization):
#     url = f"https://wogrli5cm6.execute-api.ap-south-1.amazonaws.com/api-patient-otp-dev/conversation/{conversation_id}"
#     headers = {
#         'x-tenant-id': 'SELF',
#         'Authorization': authorization,
#         'x-op': 'get-conversation'
#     }
#     response = requests.get(url, headers=headers)
#     print("record response", response.text)
#     return response.json()

# def create_record(conversation_id, user_id, question, answer, authorization):
#     print("🚀 create_record called")
#     url = "https://wogrli5cm6.execute-api.ap-south-1.amazonaws.com/api-patient-otp-dev/conversation"
#     payload = json.dumps({
#         "conversation_id": conversation_id,
#         "conversation_type": "gemini",
#         "user_id": user_id,
#         "conversation": [{"question": question, "answer": answer, "message": ""}],
#         "file_uploads": []
#     })
#     headers = {
#         'x-tenant-id': 'SELF',
#         'Authorization': authorization,
#         'x-op': 'create-conversation',
#         'Content-Type': 'application/json'
#     }
#     response = requests.post(url, headers=headers, data=payload)
#     print("✅ Create Record Response:", response.status_code, response.text)

#     return response.json()


def get_record(conversation_id, authorization):
    url = f"https://wogrli5cm6.execute-api.ap-south-1.amazonaws.com/api-patient-otp-dev/conversation/{conversation_id}"
    headers = {
        'x-tenant-id': 'SELF',
        'Authorization': authorization,
        'x-op': 'get-conversation'
    }
    response = requests.get(url, headers=headers)
    print("record response", response.text)
    return response.json()

def create_record(conversation_id, user_id, question, answer, authorization):
    print("create_record called")
    url = "https://wogrli5cm6.execute-api.ap-south-1.amazonaws.com/api-patient-otp-dev/conversation"
    payload = json.dumps({
        "conversation_id": conversation_id,
        "conversation_type": "gemini",
        "user_id": user_id,
        "conversation": [{"question": question, "answer": answer, "message": ""}],
        "file_uploads": []
    })
    headers = {
        'x-tenant-id': 'SELF',
        'Authorization': authorization,
        'x-op': 'create-conversation',
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, data=payload)
    print(" Create Record Response:", response.status_code, response.text)
    return response.json()

def create_doctor_report(conversation_id, user_id, doctor_report, authorization, patient_report):
    url = "https://wogrli5cm6.execute-api.ap-south-1.amazonaws.com/api-patient-otp-dev/conversation"
    payload = json.dumps({
        "conversation_id": conversation_id,
        "conversation_type": "gemini",
        "user_id": user_id,
        "conversation": [{"question": "", "answer": "", "message": "","doctor_report":doctor_report,"patient_report":patient_report}],
        "file_uploads": []
    })
    headers = {
        'x-tenant-id': 'SELF',
        'Authorization': authorization,
        'x-op': 'create-conversation',
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, data=payload)
    print("Doctor report saved:", response.status_code, response.text)
    return response.json()



# ------------------- Gemini & Question Logic -------------------

def query_gemini(prompt):
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(GEMINI_API_URL, json=payload, headers=headers, timeout=10)
       
        gemini_response = response.json()

        if "candidates" in gemini_response:
            text = gemini_response["candidates"][0]["content"]["parts"][0]["text"].strip()

            # For classification responses that are expected to be plain text
            if prompt.startswith("Classify the following symptoms"):
                return text.strip()
            
            # If we're expecting a question but got plain text without JSON formatting
            if "Ask ONE best follow-up question" in prompt and not (text.startswith("{") or text.startswith("```")):
                # Convert plain text question to JSON format
                return {
                    "question": text,
                    "reason": "Auto-formatted from plain text response"
                }

            # Handle JSON in code block format (```json ... ```)
            if text.startswith("```json") and text.endswith("```"):
                text = text.replace("```json", "").replace("```", "").strip()
            
            # Handle raw JSON response
            if text.startswith("{") and text.endswith("}"):
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    print(" Could not parse JSON. Raw response:", text)
                    return {"error": "Failed to parse response", "raw_text": text}
            
            # Try to parse into JSON anyway as a fallback
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                print(" Could not parse JSON. Raw response:", text)
                # Instead of failing, convert plain text to a question format
                if "Ask ONE best follow-up question" in prompt or "ask next question" in prompt.lower():
                    return {
                        "question": text,
                        "reason": "Auto-formatted from non-JSON response"
                    }
                return {"error": "Failed to parse response", "raw_text": text}

        else:
            print(" Gemini response malformed:", gemini_response)
            return {"error": "Malformed response"}

    except Exception as e:
        print(" Gemini API error:", e)
        return {"error": str(e)}

def classify_category(symptom_context):
    prompt = (
        f"Classify the following symptoms or conversation into one of:\n"
        f"- Heart_failure\n- Tuberculosis\n- General_consultation\n\n"
        f"Input: {symptom_context}\n\nReturn only the category name."
    )
    result = query_gemini(prompt)
    # Handle both string and dict responses
    if isinstance(result, dict) and "raw_text" in result:
        return result["raw_text"]
    return result

def get_unused_questions(category, history):
    asked = {entry["question"].lower() for entry in history}
    all_qs = [q["Question"] for q in QUESTION_DATA.get(category, [])]
    return [q for q in all_qs if q.lower() not in asked]

def ask_gemini_next_question(symptoms, history, available_questions):
    history_text = "\n".join([f"Q: {h['question']}\nA: {h['answer']}" for h in history])
    question_block = "\n".join(f"- {q}" for q in available_questions)
    force_question = len(history) < 6

    if force_question:
        prompt = (
            f"You are a medical AI assistant.\n\n Patient's symptoms: {symptoms}\n Conversation so far:\n{history_text}\n\n Available follow-up questions:\n{question_block}\n\n"
            f"Ask ONE best follow-up question (avoid repetition).\n"
            f" You MUST Respond in JSON: {{\"question\": \"...\", \"reason\": \"...\"}}"
        )
    else:
        prompt = (
            f"You are a medical AI assistant.\n\nPatient's symptoms: {symptoms}\n Conversation so far:\n{history_text}\n\n"
            f"Available follow-up questions:\n{question_block}\n\n"
            f"Ask ONE best question OR if enough data, return diagnosis.\n You MUST Respond in JSON"
            f"Diagnosis format: {{\"Whom to approach\": \"...\", \"Differential diagnosis\": \"...\", \"Suggestion\": \"...\"}}"
        )
    return query_gemini(prompt)

def ask_final_diagnosis(symptoms, history):
    history_text = "\n".join([f"Q: {h['question']}\nA: {h['answer']}" for h in history])
    prompt = (
        f"You are a senior medical AI.\nPatient symptoms: {symptoms}\nConversation:\n{history_text}\n\n"
        f"Give FINAL diagnosis in JSON:\n"
        f"{{\n  \"Whom to approach\": \"...\",\n  \"Differential diagnosis\": \"...\",\n  \"Suggestion\": \"...\",\n  \"reason\": \"...\"\n}}"
    )
    return query_gemini(prompt)

def create_patient_report(symptoms, history, doctor_diagnosis):
    prompt = (
            f"Create a simplified patient report based on these symptoms and conversation:\n"
            f"Symptoms: {symptoms}\nConversation:\n" + "\n".join([f"Q: {h['question']}\nA: {h['answer']}" for h in history]) + "\n\n"
            f"Create a simplified explanation of their condition . You can mention if the condition is obstructive or restrictive but nothing else. DO NOT include differential diagnoses or detailed medical terminology. Next steps should mention consulting with a doctor. No other advice. Format as a JSON with keys: 'Condition_summary', 'Next_steps'"
    )
    return query_gemini(prompt)


# ------------------- Save Reports -------------------
def save_reports(symptoms, history, doctor_diagnosis, patient_report, conversation_id, user_id, authorization):
    report_id = uuid.uuid4().hex[:8]
    with open(f"doctor_report_{report_id}.json", "w") as f:
        json.dump({"symptoms": symptoms, "conversation": history, "diagnosis": doctor_diagnosis}, f, indent=2)
    with open(f"patient_report_{report_id}.json", "w") as f:
        json.dump({"symptoms": symptoms, "conversation": history, "simplified_information": patient_report}, f, indent=2)

    create_doctor_report(conversation_id, user_id, doctor_diagnosis, authorization)
    #create_patient_report_remote(conversation_id, user_id, patient_report, authorization)

# ------------------- Run Chat -------------------
def run_chat():
    print("\U0001fa7a Welcome to the diagnostic assistant!")
    symptoms = input("Describe your symptoms: ").strip()
    authorization = input("Enter authorization token: ").strip()
    user_id = input("Enter user ID: ").strip()

    conversation_id = str(uuid.uuid4())
    question_count = 0
    max_questions = 15
    min_questions = 6
    print("hi")
    create_record(conversation_id, user_id, "\U0001fa7a Welcome to the diagnostic assistant! Describe your symptoms:", symptoms, authorization)

    while question_count < max_questions:
        record = get_record(conversation_id, authorization)
        history = record.get("conversation", [])

        full_text = symptoms + "\n" + "\n".join(f"Q: {x['question']} A: {x['answer']}" for x in history)
        category = classify_category(full_text)
        available_qs = get_unused_questions(category, history)

        response = ask_gemini_next_question(symptoms, history, available_qs)

        if isinstance(response, dict) and 'Differential diagnosis' in response and question_count >= min_questions:
            print(f"\nDiagnosis complete after {question_count} questions.")
            patient_report = create_patient_report(symptoms, history, response)
            save_reports(symptoms, history, response, patient_report, conversation_id, user_id, authorization)
            print(f"\nSummary: {patient_report}")
            break

        if isinstance(response, dict) and "question" in response:
            question = response["question"]
            print(f"\nDoctor's Question ({question_count + 1}): {question}")
            answer = input("Patient's Answer: ").strip()
            create_record(conversation_id, user_id, question, answer, authorization)
            question_count += 1
        else:
            print("Unexpected Gemini response.")
            break

    print("\nMax questions reached. Final diagnosis in progress...")
    record = get_record(conversation_id, authorization)
    history = record.get("conversation", [])
    final_diagnosis = ask_final_diagnosis(symptoms, history)
    patient_report = create_patient_report(symptoms, history, final_diagnosis)
    save_reports(symptoms, history, final_diagnosis, patient_report, conversation_id, user_id, authorization)
    print(f"\nFinal Diagnosis:\n{final_diagnosis}")

    fetch = input("\nFetch saved reports? (y/n): ").strip().lower()
    if fetch == "y":
        print("\nDoctor Report:")
        #print(get_doctor_report(conversation_id, authorization))
        print("\nPatient Report:")
        #print(get_patient_report(conversation_id, authorization))

if __name__ == "__main__":
    run_chat()
