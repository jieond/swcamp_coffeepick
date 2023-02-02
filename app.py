from flask import Flask, render_template, request, jsonify, redirect, url_for

app = Flask(__name__)

from pymongo import MongoClient

# mac에서 에러가 나는 경우 >> 사용하고 있는 인터넷 환경에 따라 보안 관련 추가 설정 2가지 필요
# 1) certifi 패키지 설치 및 임포트
import certifi
ca = certifi.where()

# 내 mogoDB 정보 가져오기 - 패스워드, 클러스터 이름 커스텀
# 2) tlsCAFile=ca 추가
client = MongoClient('mongodb+srv://test:sparta@cluster0.cfgm0s9.mongodb.net/cluster0?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.dbsparta

@app.route('/')
def main():
   return render_template('index.html')

@app.route('/order/<int:order_num>')
def move_to_order(order_num):
   return render_template('order_page.html', order_num=order_num)

@app.route("/main", methods=["POST"])
def web_main_post():
    order_name_receive = request.form['order_name_give']
    due_receive = request.form['due_give']
    cafe_name_receive = request.form['cafe_name_give']

    if order_name_receive == "" or due_receive == "" or cafe_name_receive == "-- 매장 선택 --" or cafe_name_receive == "준비중":
        return jsonify({'msg': '모든 값을 입력해주세요','order_num':0})
    else:
        order_num = db.orders.count_documents({})+1

        doc = {
            'order_num': order_num,
            'order_name': order_name_receive,
            'due': due_receive,
            'cafe_name': cafe_name_receive
        }

        db.orders.insert_one(doc)

        return jsonify({'msg': '주문서 생성 완료!','order_num':order_num})

@app.route("/main", methods=["GET"])
def web_main_get():
    return jsonify({'msg': 'GET 연결 완료!'})

if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)