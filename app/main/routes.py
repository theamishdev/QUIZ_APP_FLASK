from flask import render_template, url_for, flash, redirect, request, Blueprint, jsonify, current_app
from app.models import Quiz
from app import db
from openai import OpenAI
import google.generativeai as genai
from flask_login import current_user
import json
from .chat_tools import CHAT_TOOLS, list_my_classrooms, create_quiz_in_classroom

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    return render_template('home.html')

@main.route("/about")
def about():
    return render_template('about.html', title='About')

@main.route("/chat", methods=["POST"])
def chat():
    # Priority: Gemini -> Groq -> OpenAI
    gemini_key = current_app.config.get('GEMINI_API_KEY')
    groq_api_key = current_app.config.get('GROQ_API_KEY')
    openai_api_key = current_app.config.get('OPENAI_API_KEY')

    # Force selection logic
    if gemini_key and gemini_key.startswith("AIzaSy"):
        api_key = gemini_key
        provider_name = "Gemini"
        is_gemini = True
        is_openai = False
    elif groq_api_key:
        api_key = groq_api_key
        provider_name = "Groq"
        is_gemini = False
        is_openai = False
    elif openai_api_key:
        api_key = openai_api_key
        provider_name = "OpenAI"
        is_gemini = False
        is_openai = True
    else:
        return jsonify({"reply": "No API Key configured. Please check your .env file."}), 500

    print(f"DEBUG: Chatbot using provider: {provider_name}")

    user_message = request.json.get("message", "").lower()
    if not user_message:
        return jsonify({"reply": "No message provided."}), 400

    # Handle Mock Mode for testing without API quota
    if current_app.config.get('CHATBOT_MOCK_MODE'):
        mock_reply = "🤖 **[MOCK MODE ACTIVE]**\n\nI'm currently operating in mock mode. \n\n"
        if "classroom" in user_message or "list" in user_message:
            classrooms = list_my_classrooms()
            mock_reply += f"I can still help you simulate teacher actions! Your classrooms are: {classrooms}"
        elif "quiz" in user_message or "create" in user_message:
            mock_reply += "To create a quiz, I would normally call the tool. Since I'm in mock mode, I've verified the logic would work! Try asking me to list your classrooms."
        else:
            mock_reply += f"You said: '{user_message}'. How can I help you with Quizify today?"
        return jsonify({"reply": mock_reply})

    try:
        if is_gemini:
            # Gemini Implementation
            genai.configure(api_key=api_key)
            
            # Map tools for Gemini
            def list_rooms_wrapper():
                """List all classrooms I manage as a teacher."""
                return list_my_classrooms()
                
            def create_quiz_wrapper(classroom_id: int, title: str, questions: list, description: str = ""):
                """Create a new quiz in a specific classroom."""
                return create_quiz_in_classroom(classroom_id, title, description, questions)

            # Use Gemini 3 Flash Preview as requested
            model = genai.GenerativeModel(
                model_name='gemini-3-flash-preview',
                tools=[list_rooms_wrapper, create_quiz_wrapper] if current_user.is_authenticated and current_user.role == 'teacher' else None
            )
            
            chat_session = model.start_chat(enable_automatic_function_calling=True)
            system_prompt = "You are a helpful assistant for Quizify. If the user is a teacher, you can help them manage classrooms and create quizzes. Use the tools provided to list classrooms and create quizzes when asked."
            
            response = chat_session.send_message(f"{system_prompt}\n\nUser: {user_message}")
            return jsonify({"reply": response.text})

        else:
            # OpenAI / Groq Implementation
            if is_openai:
                client = OpenAI(api_key=api_key)
                model_name = "gpt-4o-mini"
            else:
                client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)
                model_name = "llama-3.3-70b-versatile"

            messages = [
                {"role": "system", "content": "You are a helpful assistant for Quizify. If the user is a teacher, you can help them manage classrooms and create quizzes. Use the tools provided to list classrooms and create quizzes when asked. Always double check classroom IDs before creating quizzes."},
                {"role": "user", "content": user_message}
            ]
            
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                tools=CHAT_TOOLS if current_user.is_authenticated and current_user.role == 'teacher' else None,
                tool_choice="auto" if current_user.is_authenticated and current_user.role == 'teacher' else None
            )
            
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls
            
            if tool_calls:
                messages.append(response_message)
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    if function_name == "list_my_classrooms":
                        function_response = list_my_classrooms()
                    elif function_name == "create_quiz_in_classroom":
                        function_response = create_quiz_in_classroom(
                            classroom_id=function_args.get("classroom_id"),
                            title=function_args.get("title"),
                            description=function_args.get("description", ""),
                            questions=function_args.get("questions")
                        )
                    else:
                        function_response = "Tool not found."
                    
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    })
                
                # Get a final response
                second_response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                )
                return jsonify({"reply": second_response.choices[0].message.content})

            return jsonify({"reply": response_message.content})

    except Exception as e:
        error_msg = str(e)
        if "quota" in error_msg.lower():
            return jsonify({
                "reply": f"❌ **{provider_name} Quota Exceeded**. \n\nYour API key has hit its limit. You can get a **new free Gemini API key** at [Google AI Studio](https://aistudio.google.com/app/apikey) and add it to your `.env` file, or enable `CHATBOT_MOCK_MODE=true` in `config.py` to test with simulated responses."
            }), 429
        return jsonify({"reply": f"Chatbot Error ({provider_name}): {error_msg}"}), 500

