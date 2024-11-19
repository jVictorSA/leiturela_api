# script to delete story and them activities

from mongo_conn import db
from bson import ObjectId

def delete_story(story_id):
    obj_id = ObjectId(story_id)
    story = db.stories.find_one({'_id': obj_id})

    if story:
        for activity_id in story['activities']:
            db.activities.delete_one({'_id': ObjectId(activity_id)})

        db.stories.delete_one({'_id': obj_id})
        print("Ok")
    else:
        print("História não encontrada")

if __name__ == "__main__":
    while True:
        story_id = input("Digite o ID da história a ser deletada: ")
        delete_story(story_id)