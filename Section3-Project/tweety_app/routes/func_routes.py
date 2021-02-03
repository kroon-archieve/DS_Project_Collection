import os
import pickle
from flask import Blueprint, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from tweety_app.models import db, en, Users, Tweets, parse_records, get_all_data
from tweety_app.tweety_api import api
from sklearn.linear_model import LogisticRegression
import numpy as np

FILEPATH = './model.pkl'

func_routes = Blueprint('func_routes', __name__)

# add 트위터 유저를 새로 추가할 수 있어야 합니다.
@func_routes.route('/add', methods=["GET", "POST"])
def add():
    if request.method == "POST":
        print(dict(request.form))
        result = request.form # form 에 작성된 모든 값을 가져온다.
        # result[0] 이렇게 인덱스를 불러 오는 느낌, 대신 인덱스가 아니라, input_user에 들어간 같은 값을 찾는것.
        ## Tweepy
        new = api.get_user(screen_name = result['username'])
        tweets = api.user_timeline(screen_name = result['username'], tweet_mode ="extend")
        # breakpoint()
        # Insert data into Users Table
        # 이제 model에 있는 User라는 테이블에, 트위터에서 불러온 정보들을 저장. 
        user = Users(id = new.id)# Users()라는 클래스를 불러오고 Users.query.get(new.id) or 
        user.username = new.screen_name.casefold()
        user.full_name = new.name
        user.followers = new.followers_count
        user.location = new.location

        # user = Users(id = new.id, username=new.screen_name.casefold(), full_name=new.name, followers=new.followers_count, location=new.location)
        # breakpoint()
        db.session.add(user) # user = Users()에 저장하고

        for tw in tweets:
            tweet = Tweets.query.get(tw.id) or Tweets(id = tw.id)
            tweet.text = tw.text
            tweet.embedding = en.encode(texts = [tw.text])
            print(tw.user.id)
            tweet.user_id = tw.user.id
            # breakpoint()
            db.session.add(tweet)

        db.session.commit()
    data = Users.query.all()
    return render_template('add.html', data=data)


# get 해당 트위터 유저의 트윗들을 보여줘야 합니다.
@func_routes.route('/<username>/get')
def get(username = None):
    username = username
    id = Users.query.with_entities(Users.id).filter(Users.username == username).first()
    
    data = Tweets.query.filter(Tweets.user_id == id[0]).all()

    for tweet in data:
        print(tweet.text)

    return render_template('get.html', data = data)


@func_routes.route('/gettweets', methods=["GET", "POST"])
def gettweets():
    tweets = []
    myuser = Users.query.all()
    username = ''
    if request.method == "POST":
        print(dict(request.form))
        result = request.form
        username = result['username'] # 내가 선택한 유저를 가져오는 코드 -가연님-
        id = Users.query.filter_by(username=username).first().id # 가연님  
        data = Tweets.query.filter(Tweets.user_id == id).all() # 내가 선택한 유저의 트윗을 가져옴 -가연님-
        # datas = get_all_data()
        for tweet in data:
            tweets.append(tweet.text)
    return render_template("gettweets.html", datas = myuser, data=tweets, description=username)


# delete 해당 트위터 유저를 삭제해야 합니다.
@func_routes.route('/delete', methods=['GET', 'POST'])
def delete_try(username=None):
    if request.method == "POST":
        user_info = dict(request.form)
        username = user_info['selected_user']

        user_info = Users.query.filter_by(username=username).one()
        user_id = user_info.__dict__['id']
        Tweets.query.filter_by(user_id=user_id).delete()
        Users.query.filter_by(username=username).delete()

        db.session.commit()

        data = get_all_data()
        description = f"'{username}' has been deleted."
        return render_template('delete.html', description=description, data=data)
    else:
        data = get_all_data()
        return render_template('delete.html',data=data)


def change_name(selected_user):
    if selected_user['name_type'] == 'full_name':
        Users.query.filter_by(username=selected_user['selected_user']).update(
            {'full_name': selected_user['change_name']})
        db.session.commit()
        return True

    # 입력한 username이 목록에 있는지 확인 후 없을 때만 변경
    else:
        Users.query.filter_by(username=selected_user['selected_user']).update(
            {'username': selected_user['change_name']})
        db.session.commit()
        return True

# update (Edit Value)
@func_routes.route('/update', methods=["GET", "POST"])
def update():
    if request.method == "POST":
        user_change_info = dict(request.form)
        print(user_change_info)
        # breakpoint()
        # 입력한 username이 중복된 경우와 중복되지 않은 경우 분류
        if change_name(user_change_info):
            data = get_all_data()
            return render_template('update.html', data=data)
        else:
            data = get_all_data()
            faild_name = user_change_info['name_type']
            description = f"[Failed: {faild_name}] Username cannot be duplicated. Please check again."
            return render_template('users.html', description=description, data=data)
    else:
        data = get_all_data()
        return render_template('update.html', data=data)
# ----------------------------------
# @func_routes.route('/compare/', methods=["GET", "POST"])
# def compare():
#     users = Users.query.all()
#     text = []
#     id = []

#     if request.method == "POST":
#         print(dict(request.form))
#         result = request.form

#         # import all datas from the table
#         for user in users:
#             tweets = Tweets.query.with_entities(Tweets.embedding).filter(Tweets.user_id == user.id).all()
#             for tweet in tweets:
#                 append_to_with_label(text, tweet, id, user.id)
            
#         # 3D array to 2D array
#         text_array = np.array(X)

#         nsamples, nx, ny = text_array.shape

#         text_2d = text_array.reshape(nsamples, nx * ny)

#         # Model import
#         if os.path.isfile(FILEPATH):
#             model = pickle.load(open('model.pkl', 'rb'))
#             pred_id = model.predict(en.encode(texts = [result['text']]))
#             prediction = int(pred_id[0])

#         else:
#             model = LogisticRegression(warm_start=True)
#             model.fit(text_2d, id)
#             pred_id = model.predict(en.encode(texts = [result['text']]))
#             prediction = int(pred_id[0])
#             pickle.dump(model, open('model.pkl', 'wb'))

#     # Predction result
#     pred_res = Users.query.filter(Users.id == prediction).first()


#     return render_template('compare.html', data = pred_res)
# -------------------------
# @func_routes.route('/compare/', methods=['GET', 'POST'])
# def compare():
#     result = ''
#     selected_user = ''
#     if request.method == "POST":
#         compare_info = dict(request.form)
#         print(compare_info)

#         # 서로 다른 user를 선택했을 때만 실행되도록 함
#         if compare_info['selected_user1'] != compare_info['selected_user2']:
#             user_class = compare_user(compare_info)
#             selected_user1 = compare_info['selected_user1']
#             selected_user2 = compare_info['selected_user2']
#             input_msg = compare_info['input_msg']
#             selected_user = f'[{selected_user1}, {selected_user2}] '
#             result = f'The final prediction value for "{input_msg}" is {user_class}'
#         else:
#             result = '[Failed] Please select two different users.'

#     data = get_all_data()
#     return render_template('compare.html', data=data, result=result, selected_user=selected_user)


# def compare_user(compare_info):
#     user_list = sorted([compare_info['selected_user1'], compare_info['selected_user2']])
#     user1 = user_list[0]
#     user2 = user_list[1]
#     input_msg = compare_info['input_msg']

#     user1_id = Users.query.filter_by(username=user1).one().__dict__['id']
#     user2_id = Users.query.filter_by(username=user2).one().__dict__['id']
#     file_name = f'{user1_id}_{user2_id}.pkl'
#     file_path = os.path.join(os.path.dirname(__file__), 'logistic_models', file_name)

#     # 모델이 없다면 모델 생성
#     if os.path.isfile(file_path) == False:
#         create_new_model(user1, user2, file_path)

#     with open(file_path, 'rb') as f:
#         classifier = pickle.load(f)

#     input_msg_embedding = en.encode(texts=[input_msg])
#     pred_user_id = classifier.predict(input_msg_embedding)[0]
#     pred_user = Users.query.filter_by(id=int(pred_user_id)).one().username

#     return pred_user

# def create_new_model(user1, user2, file_path):
#     X = []
#     y = []

#     user1_id = Users.query.filter_by(username=user1).first().id
#     user1_tweet_list = Tweets.query.filter_by(Tweets.user_id == user1_id).one()
#     for tweet in user1_tweet_list:
#         X.append(Tweets.embedding)
#         y.append(user1_id)

#     user2_id = Users.query.filter_by(username=user2).first().id
#     user2_tweet_list = Tweets.query.filter_by(Tweets.user_id == user2_id).one()
#     for tweet in user2_tweet_list:
#         X.append(Tweets.embedding)
#         y.append(user2_id)

#     classifier = LogisticRegression()
#     classifier.fit(X, y)

#     with open(file_path, 'wb') as f:
#         pickle.dump(classifier, f)
#----
@func_routes.route('/compare', methods=['GET', 'POST'])
def compare():
    message = ''
    if request.method == "POST":
        print(dict(request.form))
        X = []
        y = []
        

        comparing = request.form
        user1 = comparing['selected_user1']
        user2 = comparing['selected_user2']
        text_to_compare = comparing['input_msg']
        
        user1_tweet_list = Users.query.filter_by(username=user1).one().tweets
        user1_id = Users.query.filter_by(username=user1).one().id
        
        for tweet in user1_tweet_list:
            X.append(tweet.embedding)
            y.append(user1_id)
        
        user2_tweet_list = Users.query.filter_by(username=user2).one().tweets
        user2_id = Users.query.filter_by(username=user2).one().id
        
        for tweet in user2_tweet_list:
            X.append(tweet.embedding)
            y.append(user2_id)
        
        # breakpoint()
        text_array = np.array(X)

        nsamples, nx, ny = text_array.shape

        text_2d = text_array.reshape(nsamples, nx * ny)
        
        classifier = LogisticRegression()
        classifier.fit(text_2d, y)
        
        em_pred_val = en.encode(texts=[text_to_compare])
        pred_result = classifier.predict(em_pred_val)
        
        user_info = Users.query.filter_by(id=int(pred_result)).one()
        user_name = user_info.__dict__['username']
        message = f"{user_name}' is more likely to tweet '{text_to_compare}'. "
        
    data = Users.query.all()
    return render_template("compare.html", data=data, message=message)

