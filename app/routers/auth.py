from typing import Annotated
from fastapi.routing import APIRouter
from fastapi import Body, Depends, Form
from fastapi.security import OAuth2PasswordRequestFormStrict

from app.dependencies import SessionDep, get_session

router = APIRouter(
    tags=["authentication"],
    responses={401: {"description": "Unauthorized"}}
)

@router.post("/register")
async def create_user():
    pass

# take in the user data as form data
# UserModel should take in and validate email, password(length> 12char), name(length>0)
# db lookup email and see if it already exists. (index)
# hash the user password and store in db with email and name
# install pwdlib[argon2] for use in hashing
# 200 -> returns a bearer token
# 422 -> user did not submit all the required data
# 404 -> user supplies additional path or query arguments

#registration
# a user supplies username and email and password
# check if username is unique
# check if email is unique
# if group(unique)
#   hash(password)
# else
# throw email/username NOT unique exception
# store User(unique) in database
# refresh user
# return JWT token to be used for authentication

# login - a user is already registered
# a user supplies username and password
# check username exists in database
# if username
# check hash(password) in db
# else
# check hash(dummypassword) so each request takes the same amount of time and attacks cannot figure out
# which usernames are in the database and which are not

# get_current_user method
# this method is used to s