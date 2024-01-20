import awsgi
from flask import Flask, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)
BASE_URL = "https://app.ylytic.com/ylytic/test"


def fetch_comments():
    response = requests.get(BASE_URL)
    if response.status_code == 200:
        return response.json().get('comments', [])
    else:
        return []


def parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%d-%m-%Y')
    except (ValueError, TypeError):
        return None


def filter_comments(comments, filters):
    filtered_comments = comments

    if 'search_author' in filters and filters['search_author']:
        filtered_comments = [comment for comment in filtered_comments if filters['search_author'].lower() in comment['author'].lower()]

    if 'at_from' in filters and 'at_to' in filters:
        at_from = parse_date(filters['at_from'])
        at_to = parse_date(filters['at_to'])
        if at_from and at_to:
            filtered_comments = [comment for comment in filtered_comments if comment['at'] and at_from <= datetime.strptime(comment['at'], '%a, %d %b %Y %H:%M:%S %Z') <= at_to]

    if 'like_from' in filters and 'like_to' in filters:
        like_from = filters['like_from']
        like_to = filters['like_to']
        if like_from is not None and like_to is not None:
            filtered_comments = [comment for comment in filtered_comments if comment['like'] is not None and int(like_from) <= comment['like'] <= int(like_to)]

    if 'reply_from' in filters and 'reply_to' in filters:
        reply_from = filters['reply_from']
        reply_to = filters['reply_to']
        if reply_from is not None and reply_to is not None:
            filtered_comments = [comment for comment in filtered_comments if comment['reply'] is not None and int(reply_from) <= comment['reply'] <= int(reply_to)]

    if 'search_text' in filters and filters['search_text']:
        filtered_comments = [comment for comment in filtered_comments if filters['search_text'].lower() in comment['text'].lower()]

    return filtered_comments


@app.route('/search', methods=['GET'])
def search_comments():
    comments = fetch_comments()

    search_author = request.args.get('search_author')
    at_from = request.args.get('at_from')
    at_to = request.args.get('at_to')
    like_from = request.args.get('like_from')
    like_to = request.args.get('like_to')
    reply_from = request.args.get('reply_from')
    reply_to = request.args.get('reply_to')
    search_text = request.args.get('search_text')

    filters = {
        'search_author': search_author,
        'at_from': at_from,
        'at_to': at_to,
        'like_from': like_from,
        'like_to': like_to,
        'reply_from': reply_from,
        'reply_to': reply_to,
        'search_text': search_text
    }

    filtered_comments = filter_comments(comments, filters)

    return jsonify({'comments': filtered_comments})

def lambda_handler(event, context):
    return awsgi.response(app, event, context)

if __name__ == '__main__':
    app.run(debug=True)
