import json

class Trip:
    def __init__(self, trip_name):
        self.trip_name = trip_name
        self.users = []
        self.transactions = []

    def add_user(self, user):
        self.users.append(user)
        save_trips()


    def remove_user(self, user_name):
        user_to_remove = None
        for user in self.users:
            if user.name == user_name:
                user_to_remove = user
                break
        
        if user_to_remove:
            self.users.remove(user_to_remove)
        else:
            print(f"User with name '{user_name}' not found.")
        save_trips()

    def add_transaction(self, transaction, user):
        user_found = None
        for u in self.users:
            if u.name == user.name:
                user_found = u
                break

        if user_found:
            self.transactions.append(TransactionRecord(transaction, user_found))
        else:
            print("User not found!")

        save_trips()

    def get_user_transactions(self, user):
        user_transactions = []
        for transaction_record in self.transactions:
            if transaction_record.user.name == user.name:
                user_transactions.append(transaction_record.transaction)
        return user_transactions

    def total_money_paid_by_user(self, user):
        total = 0
        for trans, trans_user in self.transactions:
            if trans_user.name == user.name:
                total += trans.amount
        return total

    def remove_transaction(self, transaction):
        if transaction in self.transactions:
            self.transactions.remove(transaction)
        save_trips()
        
    def to_dict(self):
        return {
            'trip_name': self.trip_name,
            'users': [user.name for user in self.users],
            'transactions': [transaction.__dict__ for transaction in self.transactions]
        }
    
    def get_all_transactions(self):
        return self.transactions

    @classmethod
    def from_dict(cls, trip_dict):
        trip = cls(trip_dict['trip_name'])
        for user_name in trip_dict['users']:
            trip.add_user(User(user_name))
        for trans_dict in trip_dict['transactions']:
            trip.add_transaction(Transaction(**trans_dict))
        return trip


class User:
    def __init__(self, name):
        self.name = name


class Transaction:
    def __init__(self, description, amount, paid_by):
        self.description = description
        self.amount = amount
        self.paid_by = paid_by  # Guarda el nombre del usuario que pagó

    def to_dict(self):
        return {
            'description': self.description,
            'amount': self.amount,
            'paid_by': self.paid_by
        }


class TransactionRecord:
    def __init__(self, transaction, user):
        self.transaction = transaction
        self.user = user

    def to_dict(self):
        return {
            'transaction': self.transaction.to_dict(),
            'user': self.user.name
        }
        
        
# Lista para almacenar los viajes
trips_list = []

# Funciones para manejar los viajes
def create_trip(trip_name):
    new_trip = Trip(trip_name)
    trips_list.append(new_trip)
    save_trips()
    return new_trip



def get_all_trips():
    return trips_list

# Función para guardar los viajes en el archivo JSON
def save_trips():
    trips_data = [trip.to_dict() for trip in trips_list]
    with open('trips.json', 'w') as file:
        json.dump(trips_data, file)

# Función para eliminar un viaje por su nombre
def delete_trip(trip_name):
    for trip in trips_list:
        if trip.trip_name == trip_name:
            trips_list.remove(trip)
            save_trips()  # Guardar los viajes actualizados en el archivo JSON después de eliminar el viaje
            break  # Romper el bucle después de eliminar el primer viaje con el nombre buscado  

def load_trips():
    try:
        with open('trips.json', 'r') as file:
            trips_data = json.load(file)
            trips_list.clear()
            for trip_dict in trips_data:
                trips_list.append(Trip.from_dict(trip_dict))
    except FileNotFoundError:
        pass

# Cargar los viajes al inicio de la aplicación
load_trips()
