# without external storage for reports
# from flask import Flask, request, jsonify
# import json
# import os
# import uuid
# from dotenv import load_dotenv

# from prototype1 import (
#     query_gemini,
#     classify_category,
#     get_unused_questions,
#     ask_gemini_next_question,
#     ask_final_diagnosis,
#     create_patient_report,
#     save_reports
# )

# load_dotenv()
# X_API_KEY = os.getenv("X_API_KEY")

# app = Flask(__name__)
# conversation_records = {}

# MIN_QUESTIONS = 5
# MAX_QUESTIONS = 15

# @app.route('/ai_conversation', methods=['POST'])
# def ai_conversation():
#     api_key = request.headers.get("x-api-key")
#     authorization = request.headers.get("authorization")
#     user_id = request.headers.get("user-id")

#     if not api_key:
#         return jsonify({"error": "API key missing"}), 401
#     if api_key != X_API_KEY:
#         return jsonify({"error": "Invalid API key"}), 403

#     try:
#         data = request.get_json()
#         conversation_id = data.get("conversation_id") or str(uuid.uuid4())
#         question_count = int(data.get("question_count", 0))
#         question = data.get("question", "")
#         user_response = data.get("user_response", "")
#         selected_category = data.get("selected_category", "")

#         if conversation_id not in conversation_records:
#             conversation_records[conversation_id] = {
#                 "symptoms": user_response,
#                 "history": [],
#                 "category": selected_category or "General_consultation"
#             }

#         record = conversation_records[conversation_id]

#         if question_count == 0:
#             # Initial prompt
#             record["history"].append({
#                 "question": "🩺 Welcome to the diagnostic assistant! Describe your symptoms:",
#                 "answer": user_response,
#                 "reason": "Initial user input to begin the diagnostic flow."
#             })
#             full_text = user_response
#             category = classify_category(full_text)
#             record["category"] = category
#             available_qs = get_unused_questions(category, [])
#             response = ask_gemini_next_question(user_response, [], available_qs)

#             return jsonify({
#                 "flag": "question",
#                 "Q": "🩺 Welcome to the diagnostic assistant! Describe your symptoms:",
#                 "conversation_logs": record["history"]
#             })

#         # Append user's response to history
#         if question:
#             record["history"].append({
#                 "question": question,
#                 "answer": user_response,
#                 "reason": ""
#             })

#         # Re-evaluate category and ask next question
#         full_text = record["symptoms"] + "\n" + "\n".join(
#             f"Q: {x['question']} A: {x['answer']}" for x in record["history"]
#         )
#         category = classify_category(full_text)
#         record["category"] = category
#         available_qs = get_unused_questions(category, record["history"])

#         # Replace the relevant section in app.py
#         response = ask_gemini_next_question(record["symptoms"], record["history"], available_qs)
#         print("Debug - Response type:", type(response), "Content:", response)  # Add this debug line

#         # Check for error in response
#         if isinstance(response, dict) and "error" in response:
#             return jsonify({
#                 "flag": "fallback",
#                 "Q": "Can you share more details about your symptoms?",
#                 "conversation_logs": record["history"],
#                 "debug_info": response  # Include error info for debugging
#             })

#         # Check for early diagnosis
#                 # Check for early diagnosis
#         if isinstance(response, dict) and 'Differential diagnosis' in response and len(record["history"]) >= MIN_QUESTIONS:
#             patient_report = create_patient_report(record["symptoms"], record["history"], response)
#             save_reports(record["symptoms"], record["history"], response, patient_report)

#             return jsonify({
#                 "flag": "diagnosis_complete",
#                 "D": (
#                     f"Based on your symptoms, I recommend consulting a {response['Whom to approach']}. "
#                     f"Possible conditions: {response['Differential diagnosis']}. "
#                     f"Next steps: {response['Suggestion']}"
#                 ),
#                 "patient_report": patient_report,
#                 "conversation_logs": record["history"]
#             })
#         # Continue the conversation with proper question handling
#         if isinstance(response, dict) and "question" in response:
#             return jsonify({
#                 "flag": "question",
#                 "Q": response["question"],
#                 "conversation_logs": record["history"]
#             })

#         # If all else fails, fallback
#         return jsonify({
#             "flag": "fallback",
#             "Q": "Can you tell me more about how these symptoms are affecting you?",  # Changed question for variety
#             "conversation_logs": record["history"],
#             "debug_info": {"raw_response": str(response)[:200]}  # Include first 200 chars of response
#         })

#     except Exception as e:
#         print(f" Error in /ai_conversation: {e}")
#         return jsonify({"error": "Internal server error"}), 500

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)


# # after adding external storage for patient & doctor reports
# from flask import Flask, request, jsonify
# import json
# import os
# import uuid
# from dotenv import load_dotenv

# from prototype1 import (
#     query_gemini,
#     classify_category,
#     get_unused_questions,
#     ask_gemini_next_question,
#     ask_final_diagnosis,
#     create_patient_report,
#     save_reports,
#     create_record,
#     run_chat
# )

# load_dotenv()
# X_API_KEY = os.getenv("X_API_KEY")

# app = Flask(__name__)
# conversation_records = {}

# MIN_QUESTIONS = 5
# MAX_QUESTIONS = 15

# @app.route('/ai_conversation', methods=['POST'])
# def ai_conversation():
#     api_key = request.headers.get("x-api-key")
#     authorization = request.headers.get("authorization")
#     user_id = request.headers.get("user-id")

#     if not api_key:
#         return jsonify({"error": "API key missing"}), 401
#     if api_key != X_API_KEY:
#         return jsonify({"error": "Invalid API key"}), 403

#     try:
#         data = request.get_json()
#         conversation_id = data.get("conversation_id") or str(uuid.uuid4())
#         question_count = int(data.get("question_count", 0))
#         question = data.get("question", "")
#         user_response = data.get("user_response", "")
#         selected_category = data.get("selected_category", "")

#         if conversation_id not in conversation_records:
#             conversation_records[conversation_id] = {
#                 "symptoms": user_response,
#                 "history": [],
#                 "category": selected_category or "General_consultation"
#             }

#         record = conversation_records[conversation_id]

#         if question_count == 0:
#             # Initial prompt
#             record["history"].append({
#                 "question": "\U0001fa7a Welcome to the diagnostic assistant! Describe your symptoms:",
#                 "answer": user_response,
#                 "reason": "Initial user input to begin the diagnostic flow."
#             })
#             full_text = user_response
#             category = classify_category(full_text)
#             record["category"] = category
#             available_qs = get_unused_questions(category, [])
#             response = ask_gemini_next_question(user_response, [], available_qs)

#             return jsonify({
#                 "flag": "question",
#                 "Q": "\U0001fa7a Welcome to the diagnostic assistant! Describe your symptoms:",
#                 "conversation_logs": record["history"]
#             })

#         # Append user's response to history
#         if question:
#             record["history"].append({
#                 "question": question,
#                 "answer": user_response,
#                 "reason": ""
#             })

#         # Re-evaluate category and ask next question
#         full_text = record["symptoms"] + "\n" + "\n".join(
#             f"Q: {x['question']} A: {x['answer']}" for x in record["history"]
#         )
#         category = classify_category(full_text)
#         record["category"] = category
#         available_qs = get_unused_questions(category, record["history"])

#         response = ask_gemini_next_question(record["symptoms"], record["history"], available_qs)
#         print("Debug - Response type:", type(response), "Content:", response)

#         if isinstance(response, dict) and "error" in response:
#             return jsonify({
#                 "flag": "fallback",
#                 "Q": "Can you share more details about your symptoms?",
#                 "conversation_logs": record["history"],
#                 "debug_info": response
#             })

#         if isinstance(response, dict) and 'Differential diagnosis' in response and len(record["history"]) >= MIN_QUESTIONS:
#             patient_report = create_patient_report(record["symptoms"], record["history"], response)
#             save_reports(
#                 symptoms=record["symptoms"],
#                 history=record["history"],
#                 doctor_diagnosis=response,
#                 patient_report=patient_report,
#                 conversation_id=conversation_id,
#                 user_id=user_id,
#                 authorization=authorization
#             )

#             return jsonify({
#                 "flag": "diagnosis_complete",
#                 "D": (
#                     f"Based on your symptoms, I recommend consulting a {response['Whom to approach']}. "
#                     f"Possible conditions: {response['Differential diagnosis']}. "
#                     f"Next steps: {response['Suggestion']}"
#                 ),
#                 "patient_report": patient_report,
#                 "conversation_logs": record["history"]
#             })

#         if isinstance(response, dict) and "question" in response:
#             return jsonify({
#                 "flag": "question",
#                 "Q": response["question"],
#                 "conversation_logs": record["history"]
#             })

#         return jsonify({
#             "flag": "fallback",
#             "Q": "Can you tell me more about how these symptoms are affecting you?",
#             "conversation_logs": record["history"],
#             "debug_info": {"raw_response": str(response)[:200]}
#         })

#     except Exception as e:
#         print(f" Error in /ai_conversation: {e}")
#         return jsonify({"error": "Internal server error"}), 500

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)
from flask import Flask, request, jsonify
import json
import os
import uuid
from dotenv import load_dotenv

from prototype1 import (
    query_gemini,
    classify_category,
    get_unused_questions,
    ask_gemini_next_question,
    ask_final_diagnosis,
    create_patient_report,
    save_reports,
    create_record,
    create_doctor_report
)

load_dotenv()
X_API_KEY = os.getenv("X_API_KEY")

app = Flask(__name__)
conversation_records = {}

MIN_QUESTIONS = 5
MAX_QUESTIONS = 15

@app.route('/ai_conversation', methods=['POST'])
def ai_conversation():
    api_key = request.headers.get("x-api-key")
    authorization = request.headers.get("authorization")
    user_id = request.headers.get("user-id")

    if not api_key:
        return jsonify({"error": "API key missing"}), 401
    if api_key != X_API_KEY:
        return jsonify({"error": "Invalid API key"}), 403

    try:
        data = request.get_json()
        conversation_id = data.get("conversation_id") or str(uuid.uuid4())
        user_response = data.get("user_response", "")
        question = data.get("question", "")
        #selected_category = data.get("selected_category", "")

        if conversation_id not in conversation_records:
            conversation_records[conversation_id] = {
                "symptoms": user_response,
                "history": [],
                "question_count": 0
            }

        record = conversation_records[conversation_id]
        question_count = record["question_count"]

        if question_count == 0:
            # Initial prompt
            initial_q = "\U0001fa7a Welcome to the diagnostic assistant! Describe your symptoms:"
            record["history"].append({
                "question": initial_q,
                "answer": user_response,
                "reason": "Initial user input to begin the diagnostic flow."
            })
            create_record(conversation_id, user_id, initial_q, user_response, authorization)
            full_text = user_response
            category = classify_category(full_text)
            record["category"] = category
            available_qs = get_unused_questions(category, [])
            response = ask_gemini_next_question(user_response, [], available_qs)

            # Save the new question to history so next turn can use it
            next_q = response["question"] if isinstance(response, dict) and "question" in response else ""
            record["last_question"] = next_q
            record["question_count"] += 1

            return jsonify({
                "flag": "question",
                "Q": initial_q,
                "conversation_logs": record["history"],
                "question_count": record["question_count"]
            })

        # Use last question from previous response if not explicitly passed
        if not question:
            question = record.get("last_question", "Unknown question")

        record["history"].append({
            "question": question,
            "answer": user_response,
        })
        create_record(conversation_id, user_id, question, user_response, authorization)
        record["question_count"] += 1

        full_text = record["symptoms"] + "\n" + "\n".join(
            f"Q: {x['question']} A: {x['answer']}" for x in record["history"]
        )
        category = classify_category(full_text)
        record["category"] = category
        available_qs = get_unused_questions(category, record["history"])

        response = ask_gemini_next_question(record["symptoms"], record["history"], available_qs)
        print("Debug - Response type:", type(response), "Content:", response)

        if isinstance(response, dict) and "error" in response:
            return jsonify({
                "flag": "fallback",
                "Q": "Can you share more details about your symptoms?",
                "conversation_logs": record["history"],
                "debug_info": response,
                "question_count": record["question_count"]
            })

        if isinstance(response, dict) and 'Differential diagnosis' in response and len(record["history"]) >= MIN_QUESTIONS:
            patient_report = create_patient_report(record["symptoms"], record["history"], response)
            create_doctor_report(conversation_id, user_id, response, authorization, patient_report)

            return jsonify({
                "flag": "diagnosis_complete",
                "D": (
                    f"Based on your symptoms, I recommend consulting a {response['Whom to approach']}. "
                    f"Possible conditions: {response['Differential diagnosis']}. "
                    f"Next steps: {response['Suggestion']}"
                ),
                "patient_report": patient_report,
                "conversation_logs": record["history"],
                "question_count": record["question_count"]
            })

        if isinstance(response, dict) and "question" in response:
            record["last_question"] = response["question"]
            return jsonify({
                "flag": "question",
                "Q": response["question"],
                "conversation_logs": record["history"],
                "question_count": record["question_count"]
            })

        return jsonify({
            "flag": "fallback",
            "Q": "Can you tell me more about how these symptoms are affecting you?",
            "conversation_logs": record["history"],
            "debug_info": {"raw_response": str(response)[:200]},
            "question_count": record["question_count"]
        })

    except Exception as e:
        print(f" Error in /ai_conversation: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
