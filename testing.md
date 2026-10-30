# Testing the Todo API

This guide explains the tests in [`app/test_main.py`](./app/test_main.py), why
they are written this way, and how to think about testing a web API as you add
features.

## What kind of tests are these?

The tests send HTTP requests through FastAPI's `TestClient` and exercise the
real route handlers, request validation, response serialization, and database
operations. They are best described as **API tests** or **small integration
tests**: they check that several parts of the application work together.

They are not traditional isolated unit tests, which usually call one function
directly while replacing its collaborators. They are also not end-to-end tests
against a deployed server: `TestClient` calls the application in-process, so
no server needs to be started and no network port is used.

This middle layer is useful for CRUD endpoints: it tests behavior close to what
an API consumer sees without depending on deployment, credentials, or a
production database.

## What is covered?

The current tests cover these endpoint behaviors:

| Behavior | What the test checks |
| --- | --- |
| List an empty collection | `GET /todos/` returns HTTP 200, an empty `data` list, and the expected `page`, `limit`, and `total` fields. |
| Create a task | `POST /todos/` returns HTTP 201 with a generated ID and the submitted title and description. |
| Reject invalid creation input | Missing required fields and a title with the wrong type return HTTP 422. |
| List existing tasks | A task created through the API appears in the list with matching fields and a total of one. |
| Get a task | `GET /todos/{id}` returns the requested task and its fields. |
| Get a missing task | The endpoint returns HTTP 404 and the expected error detail. |
| Update a task | `PUT /todos/{id}` returns the updated fields while keeping the task's ID. |
| Update a missing task | The endpoint returns HTTP 404 and the expected error detail. |
| Delete a task | `DELETE /todos/{id}` returns HTTP 204 with an empty body; a later get confirms it is gone. |
| Delete a missing task | The endpoint returns HTTP 404 and the expected error detail. |

There are **12 test cases**: the invalid-creation test is parameterized and runs
once for each of its three input examples.

## How a test is structured

Most tests follow **Arrange, Act, Assert**:

1. **Arrange**: set up any required state, such as creating a task.
2. **Act**: send the HTTP request being tested.
3. **Assert**: check the status code and relevant response or state.

For example, the update test first creates a task, then sends a `PUT`, then
checks both the response and the updated values. Creating the task through the
API instead of inserting it directly also checks that the create endpoint and
update endpoint work together.

Assertions focus on externally visible behavior: HTTP status codes, response
fields, and whether a deleted task can still be retrieved. This makes the tests
less dependent on internal implementation details, so the code can be
refactored without changing what the tests mean.

## Test database and cleanup

The `client` fixture in `app/test_main.py` creates a fresh in-memory SQLite
database for each test. It creates the SQLModel tables, then overrides the
application's `get_session` dependency so requests use that temporary database
instead of the configured application database.

This is important because tests should not create, change, or delete real user
data. The fixture also restores any previous dependency override and disposes
of its database engine in a `finally` block. As a result, cleanup still runs
when a test fails, and one test's data does not leak into another.

`StaticPool` keeps the in-memory SQLite database on a single shared connection.
Without it, different connections can behave like separate in-memory
databases; the test client and database session need to see the same tables and
records.

The dependency override is a form of **test double**: it replaces the
production database-session provider, but the tests still use real SQLModel
sessions and a real SQLite database. That gives useful database behavior while
keeping test data isolated and fast.

## HTTP and response concepts

- **Status codes are part of the API contract.** `200` means a successful
  request with a response, `201` means a resource was created, `204` means
  success with no response body, `404` means the requested task was not found,
  and `422` means FastAPI rejected the request input.
- **A request body** is the JSON data sent with `POST` or `PUT`. The API's
  `TodoTaskCreate` schema requires a string `title` and `description`.
- **Response validation** with `TodoTaskPublic.model_validate(...)` and
  `TodoDataResponse.model_validate(...)` checks that returned JSON can be
  parsed into the expected Pydantic models. Explicit field assertions are also
  used because a valid shape alone does not prove that the endpoint returned
  the correct values.
- **The `204` check is special:** a no-content response must have no body, so
  the delete test checks `response.content == b""` rather than trying to parse
  JSON.
- The routes are declared with a trailing slash (for example, `/todos/` for
  collection routes); the tests use those declared URLs directly.

## Why the `create_task` helper exists

`create_task` sends a create request, asserts that creation succeeded, and
parses the response as `TodoTaskPublic`. Tests that need existing data can use
it without repeating setup code. It also makes a failure during setup clear:
the test fails at creation rather than producing a confusing later failure.

The helper does not replace assertions in each test. Each test still checks the
specific behavior it is responsible for.

## A bug the tests exposed

While writing these tests, the first create request exposed that the endpoint
was trying to add the request schema directly to the database session. A
request schema is for validating input; it is not the mapped database table
model. The endpoint now converts it to `TodoTask` before saving it.

That also required the table model's generated ID to default to `None`, which
lets the database assign the ID on insert. The create test protects this
behavior by checking that a created task receives a positive ID.

This illustrates a major benefit of tests: a test can reveal a defect in the
application, not just verify code that already works.

## Running the tests

From the repository root in PowerShell, run:

```powershell
.\.venv\Scripts\python.exe -m pytest app\test_main.py -q
```

The `-q` option makes pytest output shorter. A passing run prints one dot per
test and a summary such as `12 passed`. If a test fails, pytest reports the
test name, the failed assertion, and the expected and actual values.

To run all tests discovered by pytest, omit the test-file path:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Good practices used here

- **Isolation:** tests use a temporary database, not the configured application
  database.
- **Repeatability:** every test gets fresh database state, so results do not
  depend on test order or old records.
- **Cleanup:** temporary resources and dependency overrides are cleaned up even
  after a failure.
- **Behavior-focused assertions:** tests check API-visible outcomes rather
  than private implementation details.
- **Positive and negative cases:** both successful requests and common errors
  are covered.
- **Input variation:** `pytest.mark.parametrize` reuses one test for several
  invalid payloads, keeping the cases consistent without duplicating test code.
- **Explicit status and data checks:** a response is not considered correct
  merely because the request did not raise an exception.

## What is not covered yet

Tests are a safety net, not proof that every possible input or environment
works. Useful next additions as the API grows include:

- updating with missing or incorrectly typed fields;
- invalid path IDs, such as non-numeric IDs;
- creating multiple tasks and checking their ordering and aggregate count;
- checking that a rejected create or update leaves database data unchanged;
- pagination behavior, if pagination becomes configurable;
- database failures and any authentication or authorization rules that are
  added later.

The current list test checks the `page` and `limit` response fields, but the
route currently returns all tasks and hard-codes those values. It does **not**
prove that pagination is implemented.

When adding a test, first describe the contract in plain language: given a
particular request and initial state, what status code, response, or state
change should a client observe? Then write the request and assertions that
prove that contract.
