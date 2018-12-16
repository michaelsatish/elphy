from flask import render_template, session
from mongoengine.errors import DoesNotExist
from mongoengine.context_managers import switch_collection

from . import dashboard
from ..models import Project, Test


@dashboard.route('/projects/<project_name>/releases/<release_name>')
def index(project_name, release_name):
    """
    Display the overall status of the release

    Cards:
    # Total number of tests
    # Total number of passed tests
    # Total number of failed tests
    # Total number of warning tests

    Graphs:
    # Pie chart showcasing passed, failed and warning percentage
    # Bar chart showcasing number of passed, failed and warning tests

    :raises 404: If project not in collection
    :raises 404: If project in collection but release not in releases
    """

    # Return 404 if project not in collection
    # Return 404 if project in collection but release not in releases
    try:
        project = Project.objects.get(name=project_name)
        releases = Project.objects.filter(name=project.name).distinct('releases.name')
        if release_name not in releases:
            return render_template('404.html'), 404
    except DoesNotExist:
        return render_template('404.html'), 404

    collection_name = f'{project_name}_{release_name}'
    with switch_collection(Test, collection_name) as TestCollection:
        tests = []
        numbers = set(TestCollection.objects.distinct('number'))
        modules = TestCollection.objects.distinct('module')

        # Filtering to remove the older tests and keep the latest rerun
        # The latest run test picked up from tests with same number
        for num in numbers:
            test = TestCollection.objects.filter(number=num)
            latest_run_date = max(t.date for t in test)
            tests.append(
                [t for t in test if t.date == latest_run_date][0]
            )

        statuses = [test.status for test in tests]

        # Store the modules name and collection name in session
        # Used in module route to query the collection and populate sidenav
        session['modules'] = modules
        session['collection_name'] = collection_name

        total_tests = len(tests)
        total_passed = statuses.count('Passed')
        total_failed = statuses.count('Failed')
        total_warning = statuses.count('Warning')

        return render_template(
            'index.html',
            total_tests=total_tests,
            total_passed=total_passed,
            total_failed=total_failed,
            total_warning=total_warning,
            modules=modules
        )


@dashboard.route('/module/<name>')
def module(name):
    """
    Display the overall status of the Module in the release

    Cards:
    # Total number of tests
    # Total number of passed tests
    # Total number of failed tests
    # Total number of warning tests

    Table:
    Show the test number, description and status
    """

    modules = session['modules']
    collection_name = session['collection_name']

    # Store the module name in session
    # Used in test route to query the collection
    session['module'] = name

    with switch_collection(Test, collection_name) as TestCollection:
        tests_to_tablize = []
        module_tests = TestCollection.objects.filter(module=name)
        numbers = set(t.number for t in module_tests)

        # Filtering to remove the older tests and keep the latest rerun
        # The latest run test picked up from tests with same number
        for num in numbers:
            test = list(filter(lambda t: t.number == num, module_tests))
            latest_run_date = max(t.date for t in test)
            tests_to_tablize.append(
                [t for t in test if t.date == latest_run_date][0]
            )

        statuses = [test.status for test in tests_to_tablize]

        total_tests = len(tests_to_tablize)
        passed = statuses.count('Passed')
        failed = statuses.count('Failed')
        warning = statuses.count('Warning')

        return render_template(
            'module.html',
            total_tests=total_tests,
            passed=passed,
            failed=failed,
            warning=warning,
            modules=modules,
            tests=tests_to_tablize
        )


@dashboard.route('/test/<number>')
def test(number):
    """Render the Test"""

    module = session['module']
    collection_name = session['collection_name']

    with switch_collection(Test, collection_name) as TestCollection:
        tests = TestCollection.objects(
            module=module,
            number=number
        )

        if len(tests) == 1:
            return render_template(
                'test.html',
                test=tests[0]
            )
