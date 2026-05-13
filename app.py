from flask import Flask, render_template, request, redirect, url_for, session
from agent import agent
import uuid

app = Flask(__name__)
app.secret_key = 'your_secret_key'


@app.route('/')
def home():

    if 'thread_id' not in session:
        session['thread_id'] = str(uuid.uuid4())

    if 'messages' not in session:
        session['messages'] = []

    return render_template(
        'chat.html',
        messages=session['messages']
    )


@app.route('/send', methods=['POST'])
def send():

    user_message = request.form['message']

    user_lat = request.form.get('latitude')
    user_lon = request.form.get('longitude')

    if user_lat and user_lon:
        session['user_location'] = {
            'lat': user_lat,
            'lon': user_lon
        }

    response = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        },
        {
            "configurable": {
                "thread_id": session['thread_id']
            }
        }
    )

    ai_message = (
        response['messages'][-1].content
        if response.get('messages')
        else "No response"
    )

    session['messages'].append({
        'type': 'human',
        'content': user_message
    })

    session['messages'].append({
        'type': 'ai',
        'content': ai_message
    })

    session.modified = True

    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
