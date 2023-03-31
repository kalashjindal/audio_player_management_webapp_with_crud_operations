from flask import Flask, jsonify, request, render_template,redirect,url_for
import pandas as pd
from sqlalchemy import create_engine

app = Flask(__name__)

# SQLAlchemy configuration
db_uri = 'mysql://root:kalash@localhost/audio'
engine = create_engine(db_uri)

# Models
class Audio:
    @classmethod
    def add(cls, title, artist, album, genre, length):
        data = {'title': title, 'artist': artist, 'album': album, 'genre': genre, 'length': length}
        df = pd.DataFrame(data, index=[0])
        df.to_sql('audio', con=engine, if_exists='append', index=False)

    @classmethod
    def get_all(cls):
        query = 'SELECT * FROM audio'
        df = pd.read_sql(query, con=engine)
        return df.to_dict(orient='records')

    @classmethod
    def get_by_id(cls, id):
        query = f'SELECT * FROM audio WHERE id={id}'
        df = pd.read_sql(query, con=engine)
        if len(df) > 0:
            return df.iloc[0].to_dict()
        else:
            return None


class User:
    @classmethod
    def add(cls, username, password):
        data = {'username': username, 'password': password}
        df = pd.DataFrame(data, index=[0])
        df.to_sql('user', con=engine, if_exists='append', index=False)

    @classmethod
    def get_all(cls):
        query = 'SELECT id, username FROM user'
        df = pd.read_sql(query, con=engine)
        return df.to_dict(orient='records')
    
    @classmethod
    def get_by_username(cls, username):
        query = f'SELECT username, password FROM user where username="{username}"'
        df = pd.read_sql(query, con=engine)
        return df["password"][0]

class Playlist:
    @classmethod
    def add(cls, name, user_id):
        data = {'name': name, 'user_id': user_id}
        df = pd.DataFrame(data, index=[0])
        df.to_sql('playlist', con=engine, if_exists='append', index=False)

    @classmethod
    def get_all(cls):
        query = 'SELECT * FROM playlist'
        df = pd.read_sql(query, con=engine)
        return df.to_dict(orient='records')

    @classmethod
    def get_by_user_id(cls, user_id):
        query = f'SELECT * FROM playlist WHERE user_id={user_id}'
        df = pd.read_sql(query, con=engine)
        return df.to_dict(orient='records')

    @classmethod
    def get_by_id(cls, id):
        query = f'SELECT * FROM playlist WHERE id={id}'
        df = pd.read_sql(query, con=engine)
        if len(df) > 0:
            return df.iloc[0].to_dict()
        else:
            return None
    
    @classmethod
    def add_audio(cls, playlist_id, audio_id):
        data = {'playlist_id': playlist_id, 'audio_id': audio_id}
        df = pd.DataFrame(data, index=[0])
        df.to_sql('audio_playlist', con=engine, if_exists='append', index=False)

    @classmethod
    def get_audios(cls, playlist_id):
        query = f'SELECT * FROM audio_playlist JOIN audio ON audio_playlist.audio_id = audio.id WHERE playlist_id={playlist_id}'
        df = pd.read_sql(query, con=engine)
        return df.to_dict(orient='records')


# Routes
@app.route('/')
def index():
    return render_template('based.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        pass1 = User.get_by_username(username)
        if pass1==password:
            return render_template('base.html', message='Logged In')
        else:
            return render_template('based.html', message='Invalid username or password')
    else:
        return render_template('based.html')
    
    
@app.route('/add-audio/', methods=['GET', 'POST'])
def add_audio():
    if request.method == 'POST':
        data = request.form
        Audio.add(data['title'], data['artist'], data['album'], data['genre'], data['length'])
        return render_template('add_audio.html')
    else:
        return render_template('add_audio.html', message='Audio added successfully')

@app.route('/view-audio/', methods=['GET'])
def view_audio():
    audio_list = Audio.get_all()
    return render_template('view_audio.html', audio_list=audio_list)

@app.route('/view-audio/<id>/', methods=['GET'])
def view_audio_by_id(id):
    audio = Audio.get_by_id(id)
    if audio:
        return render_template('view_audio.html', audio_list=[audio])
    else:
        return jsonify({'message': 'Audio file not found'})

@app.route('/add-user/', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        data = request.form
        print(",",data)
        User.add(data['username'], data['password'])
        return render_template('add_user.html', message='User added successfully')
    else:
        return render_template('add_user.html')

@app.route('/view-users/', methods=['GET'])
def view_users():
    user_list = User.get_all()
    return render_template('view_users.html', user_list=user_list)

@app.route('/add-playlist/', methods=['GET', 'POST'])
def add_playlist():
    if request.method == 'POST':
        data = request.form
        Playlist.add(data['name'], data['user_id'])
        user_list = User.get_all()
        return render_template('add_playlist.html', user_list=user_list, message='Playlist added successfully')
    else:
        user_list = User.get_all()
        return render_template('add_playlist.html', user_list=user_list)
    
    
@app.route('/view-playlists/', methods=['GET'])
def view_playlists():
    playlist_list = Playlist.get_all()
    return render_template('view_playlists.html', playlist_list=playlist_list)

@app.route('/add-audio-to-playlist/', methods=['GET', 'POST'])
def add_audio_to_playlist():
    if request.method == 'POST':
        playlist_id = request.form['playlist_id']
        return redirect(url_for('add_audio_to_playlist_for_playlist', playlist_id=playlist_id))
    else:
        playlists = Playlist.get_all()
        return render_template('select_playlist.html', playlists=playlists)

@app.route('/add-audio-to-playlist/<int:playlist_id>/', methods=['GET', 'POST'])
def add_audio_to_playlist_for_playlist(playlist_id):
    if request.method == 'POST':
        audio_id = request.form.get('audio_id')
        Playlist.add_audio(playlist_id, audio_id)
        playlist = Playlist.get_by_id(playlist_id)
        audio_list = Playlist.get_audios(playlist_id)
        return render_template('playlist.html', playlist=playlist, audio_list=audio_list, message='Audio added successfully')
    else:
        playlist = Playlist.get_by_id(playlist_id)
        audio_list = Audio.get_all()
        return render_template('add_audio_to_playlist.html', playlist=playlist, audio_list=audio_list)

@app.route('/playlist/<int:playlist_id>')
def get_playlist_by_id(playlist_id):
    playlist = Playlist.get_by_id(playlist_id)
    if not playlist:
        abort(404)
    audio_list = Playlist.get_audios(playlist_id)
    return render_template('playlist.html', playlist=playlist, audio_list=audio_list)

@app.route('/delete-audio/<int:id>', methods=['POST'])
def delete_audio(id):
    audio = Audio.get_by_id(id)
    if audio:
        # Delete audio from playlist_audio table
        engine.execute(f"DELETE FROM playlist_audio WHERE audio_id={id}")
        # Delete audio from audio table
        engine.execute(f"DELETE FROM audio WHERE id={id}")
        return redirect(url_for('view_audio'))
    else:
        return jsonify({'message': 'Audio file not found'})

@app.route('/delete-user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    # delete user by id
    query = f'DELETE FROM user WHERE id={user_id}'
    engine.execute(query)
        
    # redirect to view users page
    return redirect(url_for('view_users'))

@app.route('/delete-playlist/<int:playlist_id>', methods=['POST'])
def delete_playlist(playlist_id):
    playlist = Playlist.get_by_id(playlist_id)
    if playlist:
        # Delete the playlist from the database
        query = f'DELETE FROM audio_playlist WHERE playlist_id={playlist_id}'
        engine.execute(query)
        query = f'DELETE FROM playlist WHERE id={playlist_id}'
        engine.execute(query)
        return redirect(url_for('view_playlists'))
    else:
        return jsonify({'message': 'Playlist not found'})


if __name__ == '__main__':
    app.run(debug=True)
