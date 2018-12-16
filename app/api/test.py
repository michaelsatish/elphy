import base64
import tempfile

from flask import jsonify, request
from jsonschema import Draft7Validator, FormatChecker
from mongoengine.context_managers import switch_collection
from mongoengine.errors import DoesNotExist

from . import api
from ..models import Project, Step, Test
from .errors import BadRequest
from .token import auth

# Schema to match Test JSON Object
schema = {
    "description": "This is a schema the matches Test JSON Object",
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "id": {
            "description": "The unique identifier for a Test",
            "type": "number"
        },
        "project": {"type": "string", "minLength": 2},
        "release": {"type": "string", "minLength": 2},
        "module": {"type": "string", "minLength": 2},
        "description": {"type": "string", "minLength": 2},
        "status": {
            "type": "string",
            "minLength": 2,
            "enum": ["Passed", "Failed", "Warning"]
        },
        "rerun": {"type": "string", "minLength": 2},
        "date": {
            "type": "string",
            "format": "date-time"
        },
        "steps": {
            "type": "array",
            "items": {"$ref": "#/definitions/step"}
        }
    },
    "required": [
        "id",
        "project",
        "release",
        "module",
        "description",
        "status",
        "steps"
    ],
    "definitions": {
        "step": {
            "type": "object",
            "required": ["description", "status"],
            "properties": {
                "description": {"type": "string", "minLength": 2},
                "status": {
                    "type": "string",
                    "minLength": 2,
                    "enum": ["Pass", "Fail", "Warn"]
                },
                "screenshot": {"type": "string", "minLength": 2},
            }
        }
    }
}


validator = Draft7Validator(
    schema=schema,
    format_checker=FormatChecker()
)


@api.route('/tests/', methods=['POST'])
@auth.login_required
def new_test():
    """
    Insert new test
    The collection name is the Project and Release name separated by _
    If test exists, the test will be added and rerun field set to True

    :raises BadRequest: If test json object does not match the schema
    """
    test_json = request.json

    # Validate schema
    errors = sorted(validator.iter_errors(test_json), key=lambda e: e.path)
    if errors:
        raise BadRequest(
            message='Test JSON Object does not match schema',
            payload={
                'validators': [error.message for error in errors]
            }
        )

    # Raise BadRequest if project not in collection
    try:
        Project.objects.get(name=test_json['project'])
    except DoesNotExist:
        raise BadRequest(
            message=f'Project {test_json["project"]} does not exists in DB'
        )

    # Raise BadRequest if module not in project document
    modules = Project.objects.filter(name=test_json['project']).distinct('modules.name')
    if test_json['module'] not in modules:
        raise BadRequest(
            message=f'Module {test_json["module"]} not assigned in project document'
        )

    # Raise BadRequest if release not in project document
    releases = Project.objects.filter(name=test_json['project']).distinct('releases.name')
    if test_json['release'] not in releases:
        raise BadRequest(
            message=f'Release {test_json["release"]} not assigned in project document'
        )

    # Create collection name
    collection_name = f'{test_json["project"]}_{test_json["release"]}'

    with switch_collection(Test, collection_name) as TestCollection:
        # Add New Test
        test = Test()
        test.number = test_json['id']
        test.module = test_json['module']
        test.description = test_json['description']
        test.status = test_json['status']

        # Rerun flag
        # If test exists in database, rerun field is set to True
        try:
            TestCollection.objects.get(number=test_json["id"])
            test.rerun = True
        except DoesNotExist:
            pass

        # If date in Json, add that date to the Test
        if test_json.get('date'):
            test.date = test_json['date']

        # Append the steps
        for steps in test_json['steps']:
            step = Step()
            step.description = steps['description']
            step.status = steps['status']

            screenshot = steps.get('screenshot')
            if screenshot:
                # Decode the b64encoded string
                # Write to a temp file
                # expensive I/O if many screenshots are taken
                # Store in ImageField

                # To Do: Implement a I/O free approach
                with tempfile.TemporaryFile() as tf:
                    img_dec = base64.b64decode(screenshot)
                    img_byte = bytearray(img_dec)
                    tf.write(img_byte)
                    tf.flush()
                    tf.seek(0)
                    step.screenshot.put(tf)
            test.steps.append(step)

        # Add tags
        test.tags.append(test_json['project'])
        test.tags.append(test_json['release'])

        test._meta['collection'] = collection_name
        test.save()

        return jsonify({
            'message': f'Test {test_json["id"]} added',
            'project': test_json['project'],
            'release': test_json['release'],
            'module': test_json['module']
        }), 200
