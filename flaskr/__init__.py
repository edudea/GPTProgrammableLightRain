import os
from html import escape

from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify
from flask_socketio import SocketIO
from flaskr.arduino import ArduinoBridge
from flaskr.arduino.ArduinoBridge import FailedToExecuteError, FailedToSplitCodeError
from flaskr.chat import DescriptionToCodeTranslater
from flaskr.chat.DescriptionToCodeTranslater import ExceedsLimitsError, TranslationError
from flaskr.db import get_db, generate_id


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    from . import db
    db.init_app(app)

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    socketio = SocketIO(app)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def index():
        if request.args.get("new_chat") is None:
            latest_chat = get_db().cursor().execute(
                "SELECT * FROM chats WHERE updatedAt=(SELECT max(updatedAt) FROM chats);").fetchone()
            if latest_chat:
                return redirect(url_for('lighteffect', chat_id=latest_chat['id']))

        chat_rows = get_db().cursor().execute("SELECT * FROM chats ORDER BY updatedAt DESC").fetchall()
        chats = list(map(lambda row: Chat(row['id'], row['name'], row['createdAt'], row['updatedAt']), chat_rows))
        return render_template('pages/index.html', chat=None, chats=chats)

    @app.route('/<chat_id>')
    def lighteffect(chat_id):
        chat_row = get_db().cursor().execute("SELECT * FROM chats WHERE id=?", [chat_id]).fetchone()
        chat = Chat(chat_row['id'], chat_row['name'], chat_row['createdAt'], chat_row['updatedAt'], chat_row['deleted'])

        chat_rows = get_db().cursor().execute("SELECT * FROM chats ORDER BY updatedAt DESC").fetchall()
        chats = list(map(lambda row: Chat(row['id'], row['name'], row['createdAt'], row['updatedAt']), chat_rows))
        return render_template('pages/index.html', chat=chat, chats=chats)

    @app.route('/api/lighteffects/<id>/conversations', methods=['POST'])
    def api_description_of_lighteffect(id):
        connection = get_db()
        curser = connection.cursor()
        conversation_rows = get_db().cursor().execute("SELECT * FROM conversations WHERE chatId=?",
                                                      [id]).fetchall()
        history_conversations = list(
            map(lambda row: Conversation(row['id'], row['chatId'], row['description'], row['answer'], row['code'],
                                         row['createdAt'], row['updatedAt']), conversation_rows))
        description = request.get_json().get('description')
        conversation_id = generate_id()
        try:
            socketio.emit(f"/lighteffects/{id}/conversations/created",
                          {'id': conversation_id, 'description': description, 'lighteffect_id': id})
            conversation = DescriptionToCodeTranslater.send_description(id, conversation_id, description,
                                                                        socketio, conversations=history_conversations)
            curser.execute("INSERT INTO conversations (id, chatId, description, answer, code) VALUES (?, ?, ?, ?, ?)",
                           (conversation_id, id, description, conversation.answer, conversation.code))
            connection.commit()
            if conversation.code is not None:
                ArduinoBridge.deploy_locally(conversation.code)
            response = make_response(
                jsonify(
                    {'answer': conversation.answer, 'description': description, 'id': conversation_id}), 201)
        except ExceedsLimitsError:
            socketio.emit(f"/lighteffects/{id}/conversations/{conversation_id}/deleted",
                          {'id': conversation_id, 'lighteffect_id': id})
            response = make_response(jsonify({'message': 'Error: Reached chat limit.', 'type': 'chat.limit.reached'}),
                                     500)
        except:
            socketio.emit(f"/lighteffects/{id}/conversations/{conversation_id}/deleted",
                          {'id': conversation_id, 'lighteffect_id': id})
            response = make_response(jsonify({'message': 'Error', 'type': 'general'}), 500)
        return response

    @app.route('/api/lighteffects', methods=['POST'])
    def api_new_lighteffect():
        lighteffect_id = generate_id()
        conversation_id = generate_id()
        description = request.get_json().get('description')
        socketio.emit("/lighteffects/created",
                      {'id': lighteffect_id, 'conversationId': conversation_id, "description": description})
        try:
            connection = get_db()
            curser = connection.cursor()
            response = DescriptionToCodeTranslater.send_description(lighteffect_id, conversation_id, description, socketio,
                                                                    use_large_model=True)
            chat_name = DescriptionToCodeTranslater.get_chat_name_suggestion(description, response.answer)
            curser = curser.execute("INSERT INTO chats (id, name) VALUES (?, ?)", (lighteffect_id, chat_name))
            curser.execute("INSERT INTO conversations (id, chatId, description, answer, code) VALUES (?, ?, ?, ?, ?)",
                           (conversation_id, lighteffect_id, description, response.answer, response.code))
            connection.commit()

            if response.code is not None:
                ArduinoBridge.deploy_locally(response.code)
            response = make_response(jsonify({"href": url_for('lighteffect', chat_id=lighteffect_id)}), 201)
        except:
            socketio.emit(f"/lighteffects/{id}/conversations/{conversation_id}/deleted",
                          {'id': conversation_id, 'lighteffect_id': id})
            response = make_response(jsonify({"message", "Failed to create light effect"}), 500)
        return response

    @app.route('/api/lighteffects/<id>/conversations')
    def api_conversations_of_light_effect(id):
        conversation_rows = get_db().cursor().execute("SELECT * FROM conversations WHERE chatId=?",
                                                      [id]).fetchall()
        conversations = list(
            map(lambda row: {'id': row['id'], 'chatId': row['chatId'], 'description': escape(row['description']),
                             'answer': escape(row['answer']), 'code': escape(row['code']),
                             'createdAt': row['createdAt'],
                             'updatedAt': row['updatedAt']}, conversation_rows))
        response = make_response(jsonify(conversations), 200)
        return response

    @app.route('/chat/run/<conversation_id>', methods=['POST'])
    def conversation_run(conversation_id):
        code = get_db().cursor().execute("SELECT * FROM conversations WHERE id=?", [conversation_id]).fetchone()['code']
        try:
            ArduinoBridge.deploy_locally(code)
            response = make_response(jsonify({'message': 'Ran successful'}), 201)
        except FailedToSplitCodeError:
            response = make_response(jsonify({'message': 'Code cannot be parsed'}), 500)
        except FailedToExecuteError:
            response = make_response(jsonify({'message': 'Deployment returned an error.'}), 500)
        return response

    if __name__ == '__main__':
        socketio.run(app, debug=True)

    return app


class Chat:
    def __init__(self, id, name, created_at, updated_at, deleted=False):
        self.id = id
        self.name = name
        self.created_at = created_at
        self.updated_at = updated_at
        self.deleted = deleted


class Conversation:
    def __init__(self, id, chat_id, description, answer, code, created_at, updated_at, deleted=False):
        self.id = id
        self.chat_id = chat_id
        self.description = description
        self.answer = answer
        self.code = code
        self.created_at = created_at
        self.updated_at = updated_at
        self.deleted = deleted
