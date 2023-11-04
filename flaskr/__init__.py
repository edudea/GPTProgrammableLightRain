import os

from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify

from flaskr.arduino import ArduinoBridge
from flaskr.arduino.ArduinoBridge import FailedToExecuteError, FailedToSplitCodeError
from flaskr.chat import DescriptionToCodeTranslater
from flaskr.chat.DescriptionToCodeTranslater import ExceedsLimitsError
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
        historyConversations = list(
            map(lambda row: Conversation(row['id'], row['chatId'], row['description'], row['answer'], row['code'],
                                         row['createdAt'], row['updatedAt']), conversation_rows))
        description = request.get_json().get('description')
        try:
            conversation = DescriptionToCodeTranslater.send_description(description, historyConversations)
            conversationId = generate_id()
            curser.execute("INSERT INTO conversations (id, chatId, description, answer, code) VALUES (?, ?, ?, ?, ?)",
                           (conversationId, id, conversation.description, conversation.answer, conversation.code))
            connection.commit()
            if conversation.code is not None:
                ArduinoBridge.deploy_locally(conversation.code)
            response = make_response(
                jsonify({'answer': conversation.answer, 'description': conversation.description, 'id': conversationId}),
                201)
        except ExceedsLimitsError:
            response = make_response(jsonify({'message': 'Error: Reached chat limit.', 'type': 'chat.limit.reached'}),
                                     500)
        return response

    @app.route('/api/lighteffects', methods=['POST'])
    def api_new_lighteffect():
        connection = get_db()
        curser = connection.cursor()
        chat_id = generate_id()
        description = request.get_json().get('description')
        response = DescriptionToCodeTranslater.send_description(description)
        chat_name = DescriptionToCodeTranslater.get_chat_name_suggestion(description, response.answer)
        curser = curser.execute("INSERT INTO chats (id, name) VALUES (?, ?)", (chat_id, chat_name))
        conversation_id = generate_id()
        curser.execute("INSERT INTO conversations (id, chatId, description, answer, code) VALUES (?, ?, ?, ?, ?)",
                       (conversation_id, chat_id, response.description, response.answer, response.code))
        connection.commit()

        if response.code is not None:
            ArduinoBridge.deploy_locally(response.code)
        response = make_response(jsonify({'id': chat_id, "conversationId": conversation_id,
                                          "description": response.description, "answer": response.answer,
                                          "href": url_for('lighteffect', chat_id=chat_id)}), 201)
        return response

    @app.route('/api/lighteffects/<id>/conversations')
    def api_conversations_of_light_effect(id):
        conversation_rows = get_db().cursor().execute("SELECT * FROM conversations WHERE chatId=?",
                                                      [id]).fetchall()
        conversations = list(
            map(lambda row: {'id': row['id'], 'chatId': row['chatId'], 'description': row['description'],
                             'answer': row['answer'], 'code': row['code'], 'createdAt': row['createdAt'],
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
