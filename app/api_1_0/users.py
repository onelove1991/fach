from flask import jsonify

from . import api
from ..models import User, Post


@api.route('/user/<int:id>')
def get_user(id):
	user = User.query.get_or_404(id)
	return jsonify(user.to_json())

@api.route('/user/<int:id>/post/')
def get_user_posts(id):
	user = User.query.get_or_404(id)
	posts = Post.query.filter_by(author_id=user.id).all()
	return jsonify({'posts': [post.to_json() for post in posts]})

@api.route('/user/<int:id>/timeline/')
def get_user_followed_posts(id):
	user = User.query.get_or_404(id)
	posts = user.followed_posts.order_by(Post.timestamp.desc()).all()
	return jsonify({'post': [post.to_json() for post in posts]})