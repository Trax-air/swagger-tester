"""Api file for the pet example API.
"""

import json


pet = {
    'category': {
        'id': 42,
        'name': 'string'
    },
    'status': 'string',
    'name': 'doggie',
    'tags': [
        {
            'id': 42,
            'name': 'string'
        }
    ],
    'photoUrls': [
        'string',
        'string2'
    ],
    'id': 42
}

order = {
    'status': 'string',
    'shipDate': '2015-08-28T09:02:57.481Z',
    'complete': True,
    'petId': 42,
    'id': 42,
    'quantity': 42
}

user = {
    'username': 'string',
    'firstName': 'string',
    'lastName': 'string',
    'userStatus': 42,
    'email': 'string',
    'phone': 'string',
    'password': 'string',
    'id': 42
}


def addPet():
    return (pet, 201)


def updatePet():
    return (pet, 200)


def findPetsByStatus():
    return ([pet], 200)


def findPetsByTags():
    return ([pet], 200)


def getPetById(petId=None):
    return (pet, 200)


def updatePetWithForm(petId=None):
    return (pet, 201)


def deletePet(petId=None):
    return ('', 204)


def placeOrder():
    return (order, 200)


def getOrderById(orderId=None):
    return (order, 200)


def deleteOrder(orderId=None):
    return ('', 204)


def createUser():
    return ('', 201)


def createUsersWithArrayInput():
    return ('', 201)


def createUsersWithListInput():
    return ('', 201)


def loginUser():
    return ('', 200)


def logoutUser():
    return ('', 200)


def getUserByName(username=None):
    return (user, 200)


def updateUser(username=None):
    return (pet, 200)


def updateUserEmail(username):
    return ('+1-202-555-0153', 200)


def deleteUser(username=None):
    return ('', 204)
