from flask import g, jsonify, request, current_app, url_for
from flask.ext.httpauth import HTTPBasicAuth

from .. import db
from . import api
from .errors import forbidden
from ..models import Post, Permission
from .decorators import permission_required


auth = HTTPBasicAuth()

@api.route('/posts/')
#@auth.login_required
def get_posts():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_posts', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_posts', page=page+1, _external=True)

    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
        'count':pagination.total
        })

@api.route('/posts/<int:id>')
#@auth.login_required
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_json())

@api.route('/posts/', methods=['POST'])
@permission_required(Permission.WRITE_ARTICLES)
def new_post():
    post = Post.from_json(request.json)
    post.author = g.current_user
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()), 201, \
                {'Location': url_for('api.get_post', id=post.id, _external=True)}

@api.route('/posts/<int:id>', methods=['PUT'])
@permission_required(Permission.WRITE_ARTICLES)
def edit_post(id):
    post = Post.query.get_or_404(id)
    if g.current_user != post.author and \
            not g.current_user.can(Permission.ADMINISTER):
        return forbidden('Insufficient Permissions')
    body = request.json.get('body')
    if body:
        post.body = body
        db.session.add(post)
        db.session.commit()
    return jsonify(post.to_json())

@api.route('/posts/<int:id>/comments/')
def get_post_comments(id):
    post = Post.query.get_or_404()
    comments = post.comments
    return jsonify({'comments': [comment.to_json for comment in comments]})

@api.route('/posts/<int:id>/comments', methods=['POST'])
@permission_required(Permission.COMMENT)
def new_comment():
    post = Post.query.get_or_404()
    comment = Comment.from_json(request.json)
    comment.author = g.current_user
    comment.post = post
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_json, 201,
                    {'location': url_for(
                        'api.get_comment', id=comment.id, _external=True)})