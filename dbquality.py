import pymongo
from datetime import datetime, timedelta
from bson import ObjectId


client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['advertisement_portal']
users = db['users']
ads = db['advertisements']
archived_ads = db['archived_advertisements']
comments = db['comments']

def create_user(name, surname, registration_date, phone_number):
    user_data = {
        'name': name,
        'surname': surname,
        'registration_date': registration_date,
        'phone_number': phone_number
    }
    return users.insert_one(user_data).inserted_id

def create_advertisement(title, description, validity_days, category, user_id, additional_properties=None):
    current_datetime = datetime.now()
    advertisement_data = {
        'title': title,
        'description': description,
        'validity_date': datetime.now() + timedelta(days=validity_days),
        'category': category,
        'user_id': user_id,
        'additional_properties': additional_properties or {},
    }
    return ads.insert_one(advertisement_data).inserted_id

def create_comment(advertisement_id, user_id, text):
    comment_data = {
        'advertisement_id': advertisement_id,
        'user_id': user_id,
        'text': text,
        'timestamp': datetime.now()
    }
    return comments.insert_one(comment_data).inserted_id


user_id = create_user('Armandas', 'Jereminas', datetime.now(), '123456789')
user2_id = create_user('Nedas', 'Baranauskas', datetime.now(), '987654321')
user3_id = create_user('Ramunas', 'Rudokas', datetime.now(), '123789456')

advertisement_id = create_advertisement('BMW M3 for sale', 'Pristine condition', 30, 'Automobile', user_id, {'manufacturer': 'BMW', 'mileage': 50000, 'VIN': 'ABC123'})
advertisement2_id = create_advertisement('VW Golf for sale', 'Reliable, comfortable', 30, 'Automobile', user2_id, {'manufacturer': 'Volkswagen', 'mileage': 1000000, 'VIN': 'CBA321'})
advertisement3_id = create_advertisement('I reselling a piano I got', 'New, just shipped', 30, 'Musical Instruments', user2_id, {'brand': 'Fender', 'color': 'Dark Brown', 'condition': 'New'})
advertisement4_id = create_advertisement('Selling my old guitars', 'Used, but still works!', 30, 'Musical Instrumants', user3_id, {'brand': 'Yamaha', 'color': 'Black', 'condition': 'Used'})

comment_id = create_comment(advertisement3_id, user_id, 'Can I come pick it up now?')
comment2_id = create_comment(advertisement3_id, user3_id, 'I will pay you more to come pick it up tomorrow!')
comment3_id = create_comment(advertisement3_id, user_id, 'I will pay double the price!')

#Funkcija, kuri suranda 10 naujausiu skelbimu ir atspausdina ju informacija
def print_newest_ads():
    newest_ads = ads.find({}, {'_id': 0, 'system_data': 0}).sort('validity_date', pymongo.DESCENDING).limit(10)
    print("Naujausi skelbimai:\n")
    
    for ad in newest_ads:
        print(f"Title: {ad['title']}")
        print(f"Description: {ad['description']}")
        print(f"Category: {ad['category']}")
        
        additional_properties = ad.get('additional_properties', {})
        if additional_properties:
            print("Additional Properties:")
            for key, value in additional_properties.items():
                print(f"  {key}: {value}")

        print("------")

print_newest_ads()

print()
print()
print()
print()

#Funkcija, kuri suranda ir atspaudina 10 naujausiu skelbimu, pagal pasirinkta vartotoja
def print_newest_ads_for_user(user_id):
    newest_ads = ads.find({'user_id': user_id}, {'_id': 0, 'system_data': 0}).sort('validity_date', pymongo.DESCENDING).limit(10)
    user = users.find_one({'_id': user_id})  
    author_name = f"{user['name']} {user['surname']}"
    print(f"Naujausi, vartotojo {author_name} skelbimai:")
        
    for ad in newest_ads:
        print(f"Title: {ad['title']}")
        print(f"Description: {ad['description']}")
        print(f"Category: {ad['category']}")
            
        additional_properties = ad.get('additional_properties', {})
        if additional_properties:
            print("Additional Properties:")
            for key, value in additional_properties.items():
                print(f"  {key}: {value}")
        print("------")

print_newest_ads_for_user(user2_id)


print()
print()
print()
print()

#Funkcija, archyvuojanti skelbimus, perkelianti juos is skelbimu kolekcijos i archyvuotu skelbimu
def archive_expired_ads():
    current_datetime = datetime.now()
    expired_ads = ads.find({'validity_date': {'$lt': current_datetime}})
    for ad in expired_ads:
        archived_ads.insert_one(ad)
        ads.delete_one({'_id': ad['_id']})

archive_expired_ads()

#Funkcija, spausdinanti tam tikro vartotojo skelbimu skaiciu
def print_user_ad_count(user_id):
    user_info = users.find_one({'_id': user_id})

    if user_info:
        user_name = f"{user_info['name']} {user_info['surname']}"
        user_ad_count = ads.count_documents({'user_id': user_id})

        print(f"Total advertisements by user {user_name}: {user_ad_count}")
    else:
        print(f"User with ID {user_id} not found.")

print_user_ad_count(user2_id)

print()
print()
print()
print()

#Funkcija, kuri suranda ir atspaudina 10 naujausiu skelbimu pagal kategorija
def print_newest_ads_for_category(category):
    newest_ads = ads.find({'category': category}, {'_id': 0, 'system_data': 0}).sort('validity_date', pymongo.DESCENDING).limit(10)
    print(f"Naujausi, skelbimai pagal kategoriją: {category}")

    for ad in newest_ads:
        user_id = ad.get('user_id')
        user = users.find_one({'_id': user_id})

        author_name = f"{user['name']} {user['surname']}"
        print(f"\nAuthor: {author_name}")
        print(f"Title: {ad['title']}")
        print(f"Description: {ad['description']}")
            
        additional_properties = ad.get('additional_properties', {})
        if additional_properties:
            print("Additional Properties:")
            for key, value in additional_properties.items():
                print(f"  {key}: {value}")
        print("------")

print_newest_ads_for_category('Automobile')

print()
print()
print()
print()
db.users.drop()
db.advertisements.drop()
db.archived_advertisements.drop()
db.comments.drop()
