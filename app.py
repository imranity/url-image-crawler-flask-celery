import os
import uuid
import logging

from flask import Flask, request, render_template, session, flash, redirect, \
    url_for, jsonify, abort,make_response
from worker import celery
from celery.result import AsyncResult
import celery.states as states
import redis

env=os.environ
app = Flask(__name__)
r = redis.StrictRedis(host='redis', port=6379, db=0)
ENDPOINTS = {'post_jobs' : '/jobs', 
             'get_status' : '/jobs/<job_id>/status', 
            'get_results' : '/jobs/<job_id>/results'}

@app.route(ENDPOINTS['post_jobs'], methods=[ 'POST'])
def jobs():
    if not request.json or not 'urls' in request.json:
       abort(400)
    uid = uuid.uuid4()
    str_uid = str(uid)
    urls = request.json['urls']
    task_ids = {}
    for url in urls:
        task = celery.send_task('mytasks.crawl', args=[url], kwargs={})
        task_ids[task.id] = url
    r.hmset(str_uid, task_ids)
    return make_response(jsonify({'id': str_uid}), 202)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': "Not found", "Available Endpoints are:":ENDPOINTS.values()}), 404)

@app.route(ENDPOINTS['get_status'])
def get_status(job_id):
    status={'success':0,'inprogress':0}
    if not r.exists(job_id):
        return make_response("Job ID given doesnt exist %s \n" % job_id,404)
    task_ids = r.hgetall(job_id)
    for task_id in task_ids.keys():
        res = celery.AsyncResult(task_id)
        if res.state==states.PENDING:
            status['inprogress']+=1
        if res.state==states.SUCCESS:
            status['success']+=1
    return make_response(jsonify({'id':job_id,'status':status}),200)


@app.route(ENDPOINTS['get_results'])
def get_results(job_id):
    results = {}
    if not r.exists(job_id):
        return make_response("Job ID given doesnt exist %s \n" % job_id,404)
    task_ids = r.hgetall(job_id)
    for task_id in task_ids.keys():
        result = []
        res = celery.AsyncResult(task_id)
        if res.state==states.PENDING:
            result = []
        if res.state==states.SUCCESS:
            result = res.result
        results[task_ids[task_id]] = result
    return make_response(jsonify({'id':job_id,'results':results}),200)

if __name__ == '__main__':
    app.run(debug=env.get('DEBUG',True),
            port=int(env.get('PORT',5000)),
            host=env.get('HOST','0.0.0.0')
    )
