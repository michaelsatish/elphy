from flask import jsonify
from mongoengine.errors import DoesNotExist, NotUniqueError

from . import api
from ..models import Module, Project, Release
from .errors import BadRequest
from .token import auth


def find_project(name):
    """
    Governs project document existence before updating Modules and Releases

    :param name: Project name
    :raises BadRequest: If searched document not in project collection
    """
    try:
        return Project.objects.get(name=name)
    except DoesNotExist:
        raise BadRequest(message=f'Project {name} does not exists in Database')


@api.route('/projects/')
def get_projects():
    """Return all project names from project collection"""
    projects = Project.objects()
    return jsonify({
        'no of projects': len(projects),
        'projects': [project.name for project in projects]
    })


@api.route('/projects/<name>')
def get_project(name):
    """Return Modules and Releases information of a given project document"""
    project = find_project(name=name)
    return jsonify({
        'name': project.name,
        'modules': [module.name for module in project.modules],
        'releases': [release.name for release in project.releases]
    })


@api.route('/projects/<name>', methods=['POST'])
@auth.login_required
def new_project(name):
    """
    Insert new document in project collection

    :param name: Project name
    :raises BadRequest: If a document with project name exists
    """
    try:
        project = Project()
        project.name = name
        project.save()

        return jsonify({
            'message': 'Project added',
            'name': name
        }), 200
    except NotUniqueError:
        raise BadRequest(
            message='Insertion of project failed',
            payload={
                'validator': f'Project {name} exists in Database'
            }
        )


@api.route('/projects/<project_name>/modules/<module_name>', methods=['POST'])
@auth.login_required
def add_module(project_name, module_name):
    """
    Update project document with module name

    :param name: Project name
    :param name: Module name
    """
    project = find_project(name=project_name)

    module = Module()
    module.name = module_name
    project.update(add_to_set__modules=module)

    return jsonify({
        'message': 'Module added',
        'name': module_name
    }), 200


@api.route('/projects/<project_name>/releases/<release_name>', methods=['POST'])
@auth.login_required
def add_release(project_name, release_name):
    """
    Update project document with release name

    :param name: Project name
    :param name: Release name
    """
    project = find_project(name=project_name)

    release = Release()
    release.name = release_name
    project.update(add_to_set__releases=release)

    return jsonify({
        'message': 'Release added',
        'name': release_name
    }), 200
