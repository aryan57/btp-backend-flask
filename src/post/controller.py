from flask import jsonify, request
from src import db
from src.post import post_blueprint
from src.post.model import Post
from src.category.model import Category
from google.cloud import storage
from flask_jwt_extended import (
	jwt_required,
	get_jwt_identity,
)
import uuid

@post_blueprint.post('/uploadPostImage')
@jwt_required()
def uploadPostImage():
	file = request.files.get('file')
	if file is None or file.filename == "":
		return jsonify({'success': False,"message": "no file"})
	try:
		
		storage_client = storage.Client.from_service_account_json('credentials.json')
		bucket = storage_client.get_bucket('post-images-btp-backend')
		blob = bucket.blob(str(uuid.uuid4()))
		blob.upload_from_file(file,content_type=file.content_type)
		return jsonify({'success': True,"public_url": blob.public_url})
	
	except Exception as e:
		
		return jsonify({'success': False,"message": str(e)})

@post_blueprint.get('/ping')
@jwt_required()
def ping():
	return jsonify('OK')

@post_blueprint.post('/createPost')
@jwt_required()
def createPost():
	description = request.json.get("description")
	imgLink = request.json.get("imgLink")
	unixTime = request.json.get("unixTime")
	longitude = request.json.get("longitude")
	latitude = request.json.get("latitude")
	categoryId = request.json.get("categoryId")

	if ((imgLink==None) or (None==unixTime) or (None==longitude) or (None==latitude) or (None==categoryId)):
		return jsonify({'success': False, 'message': 'please provide all arguments'})
	
	try:
		category = Category.query.filter_by(id=categoryId).one_or_none()
	except Exception as e:
		return jsonify({'success': False, 'message': str(e)})
	
	if (not category):
		return jsonify({'success': False, 'message': 'no category found with categoryId=[{}]'.format(categoryId)})
	
	identity = get_jwt_identity()

	new_post = Post(description=description,imgLink=imgLink,unixTime=unixTime,longitude=longitude,latitude=latitude,userId=identity,categoryId=categoryId)
	try:
		db.session.add(new_post)
		db.session.commit()
	except Exception as e:
		return jsonify({'success': False, 'message': str(e)})

	return jsonify({'success': True, 'message': 'Post created successfully'})

@post_blueprint.get('/allPosts')
@jwt_required()
def allPosts():
	try:
		lst = Post.query.all()
	except Exception as e:
		return jsonify({'success': False, 'message': str(e)})

	return jsonify({'success': True, 'list': [obj.as_dict() for obj in lst]})

@post_blueprint.get('/getPost/<int:post_id>')
@jwt_required()
def getPost(post_id):
	try:
		post = Post.query.filter_by(id=post_id).one_or_none()
	except Exception as e:
		return jsonify({'success': False, 'message': str(e)})
	if (not post):
		return jsonify({'success': False, 'message': 'post with id=[{}] not present.'.format(post_id)})
	return jsonify({'success': True, 'post': post.as_dict()})