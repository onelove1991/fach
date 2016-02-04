from flask import jsonify

from . import api
from ..models import Comment, Post


@api.route('/comments/')
def get_comments():
	comments = Comment.query.all()
	return jsonify({'comments': [comment.to_json() for comment in comments]})

@api.route('/comments/<int:id>')
def get_comment(id):
	comment = Comment.query.get_or_404()
	return jsonify(comment.to_json())
