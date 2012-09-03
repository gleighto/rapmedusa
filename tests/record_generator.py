
import redis

from random import choice

def generateRecord():
    names = ['Bob', 'Rick', 'Alice', 'George', 'Henry']
    ages = ['21', '33', '19', '55', '64']
    eyes = ['brown', 'blue', 'green']
    hairColors = ['brown', 'blonde', 'black', 'red', 'grey']

    name = choice(names)
    age = choice(ages)
    eye = choice(eyes)
    hair = choice(hairColors)

    return dict({'name': name,
                 'age': age,
                 'eye': eye,
                 'hair': hair})

conn = redis.StrictRedis()

conn.delete('recInput')

for i in range(0,1000000):
    rec = generateRecord()
    conn.hset('recInput', i, rec)
    


    
