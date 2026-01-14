from flask import Flask, render_template, request, session, redirect, url_for, g, jsonify
from werkzeug.utils import secure_filename
from pathlib import Path
import os

app = Flask(__name__)
app.secret_key = "dev-secret-key"

items = [
    {
        'id': 1,
        'title': '冷蔵庫',
        'detail': '食品を冷やし保存します',
        'text': '食品を新鮮な状態で長く保存するための必須家電です。庫内は用途別に整理しやすい設計となっており、野菜や肉、飲み物などを適切な温度で管理できます。省エネ性能にも配慮されており、日常的に使っても電気代を抑えられる点が魅力です。家庭の食生活を支える心強い存在です。',
        'price': 200000,
        'file': 'nofile.png'
    },
    {
        'id': 2,
        'title': 'テレビ',
        'detail': '様々な番組を見ます',
        'text': '地上波放送から動画配信サービスまで、さまざまなコンテンツを楽しめる映像機器です。高精細な画面により、映画やスポーツ、ニュースを臨場感たっぷりに視聴できます。リビングに設置することで、家族や友人とくつろぎの時間を共有できる中心的な家電です。',
        'price': 50000,
        'file': 'nofile.png'
    },
    {
        'id': 3,
        'title': 'スマホ',
        'detail': 'アプリを利用できます',
        'text': '通話やメッセージだけでなく、アプリやインターネット、カメラ機能など多彩な用途に対応する情報端末です。日常の連絡手段としてはもちろん、仕事や学習、娯楽まで幅広く活躍します。携帯性に優れ、外出先でも必要な情報にすぐアクセスできる点が大きな特徴です。',
        'price': 100000,
        'file': 'nofile.png'
    },
    {
        'id': 4,
        'title': '洗濯機',
        'detail': '衣類を自動で洗浄・乾燥します',
        'text': '衣類の洗浄から脱水、乾燥までを自動で行う家事の強い味方です。洗濯物の量や汚れ具合に応じた運転が可能で、衣類を傷めにくく効率的に洗い上げます。毎日の洗濯作業を大幅に省力化でき、忙しい生活を支えてくれる便利な家電です。',
        'price': 150000,
        'file': 'nofile.png'
    },
    {
        'id': 5,
        'title': '電子レンジ',
        'detail': '食材を素早く温めたり調理したりします',
        'text': '食材の温め直しや簡単な調理を短時間で行える調理家電です。忙しい朝や帰宅後でも手軽に食事の準備ができ、冷凍食品や作り置きの活用にも役立ちます。操作もシンプルで、料理が苦手な方でも安心して使える点が魅力です。',
        'price': 30000,
        'file': 'nofile.png'
    },
    {
        'id': 6,
        'title': 'エアコン',
        'detail': '室内の温度と湿度を快適に保ちます',
        'text': '室内の温度や湿度を調整し、一年を通して快適な空間を保つ空調機器です。夏は涼しく、冬は暖かく過ごせるため、生活の質を大きく向上させます。省エネ性能の高いモデルを選ぶことで、快適さと電気代のバランスを両立できます。',
        'price': 120000,
        'file': 'nofile.png'
    },
    {
        'id': 7,
        'title': '掃除機',
        'detail': '床のゴミやホコリを強力に吸い取ります',
        'text': '床やカーペットにたまったゴミやホコリを効率よく吸い取る清掃家電です。細かなチリまでしっかり除去できるため、室内を清潔に保つのに役立ちます。軽量で取り回しの良い設計のものも多く、日常の掃除を手軽に行える点が特長です。',
        'price': 45000,
        'file': 'nofile.png'
    },
    {
        'id': 8,
        'title': 'ノートパソコン',
        'detail': '仕事や学習など多目的に利用できます',
        'text': '仕事、学習、プライベートまで幅広く利用できる携帯型コンピュータです。持ち運びしやすく、自宅だけでなく外出先でも作業が可能です。文書作成やオンライン会議、調べものなど、多様な用途に対応できるため、現代生活に欠かせないデバイスです。',
        'price': 180000,
        'file': 'nofile.png'
    }
]

IMG_PATH_ITEM = 'images/items/'
IMG_PATH_DROP = 'static/images/drops/'
ALLOWED_SUFFIXES = {".jpg", ".png"}
IMAGE_DIR = Path('static/images/drops')

def get_items(num = None):
    if 'items' in session:
        items_data = session['items']
    items_data = session.get('items', items)
    if num:
        return items_data[num - 1]
    return items_data

def get_images():
    return sorted(
        (
            p.relative_to("static").as_posix()
            for p in IMAGE_DIR.iterdir()
            if p.is_file() and p.suffix.lower() in ALLOWED_SUFFIXES
        ),
    reverse=True
    )

@app.route('/')
def index():
    return render_template('top.j2', items=get_items(), images=get_images())

@app.route('/list')
def item_list():
    return render_template('list.j2', items=get_items(), img_path_item=IMG_PATH_ITEM)

@app.route('/detail/<int:id>')
def item_detail(id):
    if id:
        return render_template('detail.j2', item=get_items(id), img_path_item=IMG_PATH_ITEM)
    return redirect(url_for('index'))

@app.route('/create', methods=['GET', 'POST'])
def item_create():
    if request.method == 'POST':
        return redirect(url_for('index'))
    return render_template('create.j2')

@app.route("/<int:id>", methods=["POST"])
def upload(id):
    file = request.files.get("img")
    if not file or file.filename == "":
        return redirect(url_for('item_detail', id=id))
    filename = secure_filename(file.filename)
    file.save(os.path.join(IMG_PATH_ITEM, filename))
    items[id - 1]['file'] = filename 
    session['items'] = items
    return redirect(url_for('item_detail', id=id))

@app.route("/drop", methods=["GET", "POST"])
def drop():
    if request.method == 'POST':
        if "file" not in request.files:
            return jsonify({"error": "ファイルが部分的です"}), 400
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "ファイルを選択できませんでした"}), 400
        save_path = os.path.join(IMG_PATH_DROP, file.filename)
        file.save(save_path)
        return jsonify({"success": True, "filename": file.filename})
    return render_template('drop.j2')

if __name__ == '__main__':
    app.run(debug=True)