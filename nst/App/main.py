import logging
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from backend import create_trip, delete_trip, get_all_trips, User, Transaction, Trip, TransactionRecord
from kivy.uix.gridlayout import GridLayout



class WelcomeScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        self.app_name = Label(text='EthDivider', font_size='24sp')
        self.subtitle = Label(text='Proyecto NST Juan Pontón Rodríguez', font_size='16sp')
        self.add_widget(self.app_name)
        self.add_widget(self.subtitle)

        Clock.schedule_once(self.switch_to_main_menu, 1)  # Cambiar al menú principal después de 2 segundos

    def switch_to_main_menu(self, dt):
        app = App.get_running_app()  # Obtener la instancia de la aplicación
        app.root.current = 'main_menu'  # Cambiar al menú principal


class MainMenuScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        self.app_name = Label(text='EthDivider', font_size='24sp')
        self.add_widget(self.app_name)

        self.add_trip_button = Button(text='Añadir viaje', size_hint=(1, None), height=40, background_color=(0, 0.7, 0.7, 1))
        self.add_trip_button.bind(on_release=self.show_add_trip_popup)  # Enlazar función para mostrar ventana emergente de nuevo viaje
        self.add_widget(self.add_trip_button)

        self.trips_container = BoxLayout(orientation='vertical')
        self.add_widget(self.trips_container)

        self.update_trip_list()  # Actualizar la lista de viajes

    

    def delete_trip(self, instance):
        trip_layout = instance.parent
        trip_name = trip_layout.children[1].text  # Obtener el nombre del viaje desde el segundo botón

        # Llamar a la función de backend para eliminar el viaje
        delete_trip(trip_name)

        # Eliminar el widget del viaje de la interfaz
        self.trips_container.remove_widget(trip_layout)


    def show_add_trip_popup(self, instance):
        popup = Popup(title='Añadir viaje', size_hint=(None, None), size=(300, 200))
        input_field = TextInput(multiline=False)
        confirm_button = Button(text='Confirmar', size_hint=(1, None), height=40)
        cancel_button = Button(text='Cancelar', size_hint=(1, None), height=40)

        def add_new_trip():
            trip_name = input_field.text
            if trip_name:
                create_trip(trip_name)  # Llamar a la función de backend para crear un nuevo viaje
                trip_layout = BoxLayout(size_hint=(1, None), height=40)
                trip_button = Button(text=trip_name, size_hint=(0.9, 1))
                trip_delete_button = Button(text='Eliminar', size_hint=(0.1, 1))

                trip_layout.add_widget(trip_button)
                trip_layout.add_widget(trip_delete_button)

                trip_button.bind(on_release=lambda instance: self.show_trip_transactions(trip_name))
                trip_delete_button.bind(on_release=self.delete_trip)

                self.trips_container.add_widget(trip_layout)

        confirm_button.bind(on_release=lambda instance: (add_new_trip(), popup.dismiss()))
        cancel_button.bind(on_release=popup.dismiss)

        popup.content = BoxLayout(orientation='vertical')
        popup.content.add_widget(input_field)
        buttons_layout = BoxLayout(size_hint=(1, None), height=40)
        buttons_layout.add_widget(confirm_button)
        buttons_layout.add_widget(cancel_button)
        popup.content.add_widget(buttons_layout)

        popup.open()

    def update_trip_list(self):
        trips = get_all_trips()  # Obtener todos los viajes del backend
        for trip in trips:
            trip_layout = BoxLayout(size_hint=(1, None), height=40)
            trip_button = Button(text=trip.trip_name, size_hint=(0.9, 1))
            trip_delete_button = Button(text='Eliminar', size_hint=(0.1, 1))

            trip_layout.add_widget(trip_button)
            trip_layout.add_widget(trip_delete_button)  

            # Enlazar la función solo al botón del nombre del viaje
            trip_button.bind(on_release=lambda instance, trip_name=trip.trip_name: self.show_trip_transactions(trip_name))

            trip_delete_button.bind(on_release=self.delete_trip)  # Enlazar función para eliminar viaje

            self.trips_container.add_widget(trip_layout)

    def show_trip_transactions(self, trip_name):
        # Obtener el viaje seleccionado en la lista de viajes
        selected_trip = None
        for trip in get_all_trips():
            if trip.trip_name == trip_name:
                selected_trip = trip
                break

        # Cambiar a la pantalla de transacciones del viaje seleccionado
        if selected_trip:
            trip_transactions_screen = TripTransactionsScreen(trip=selected_trip, name=f'{trip_name}_transactions')
            app = App.get_running_app()
            app.root.add_widget(trip_transactions_screen)
            app.root.current = f'{trip_name}_transactions'

            
class TripTransactionsScreen(Screen):
    def __init__(self, trip, **kwargs):
        super().__init__(**kwargs)
        self.trip = trip

        # Grid Layout para organizar los elementos
        layout = GridLayout(cols=1, spacing=10, padding=10)
        self.add_widget(layout)

        # Sección de Usuarios
        users_section = BoxLayout(orientation='vertical')
        self.users_label = Label(text='Usuarios:', font_size='16sp')
        users_section.add_widget(self.users_label)

        self.users_container = BoxLayout(orientation='vertical')
        users_section.add_widget(self.users_container)

        self.load_users()
        layout.add_widget(users_section)

        # Sección de Transacciones
        transactions_section = BoxLayout(orientation='vertical')
        self.transactions_label = Label(text=f'Transacciones de {self.trip.trip_name}', font_size='20sp')
        transactions_section.add_widget(self.transactions_label)

        self.transactions_container = BoxLayout(orientation='vertical')
        transactions_section.add_widget(self.transactions_container)

        layout.add_widget(transactions_section)

        # Botones para Usuarios
        user_buttons_section = BoxLayout(spacing=10)
        add_user_button = Button(text='Añadir Usuario')
        add_user_button.bind(on_release=self.show_add_user_popup)
        user_buttons_section.add_widget(add_user_button)

        remove_user_button = Button(text='Eliminar Usuario')
        remove_user_button.bind(on_release=self.show_remove_user_popup)
        user_buttons_section.add_widget(remove_user_button)

        layout.add_widget(user_buttons_section)

        # Botón para añadir transacción
        add_transaction_button = Button(text='Añadir Transacción')
        add_transaction_button.bind(on_release=self.show_add_transaction_popup)
        layout.add_widget(add_transaction_button)

        # Botón para volver al menú principal
        back_to_main_button = Button(text='Volver al Menú Principal')
        back_to_main_button.bind(on_release=self.go_to_main_menu)
        layout.add_widget(back_to_main_button)

        # Cargar usuarios y transacciones al iniciar
        self.load_users()
        self.load_transactions()

    def go_to_main_menu(self, instance):
        app = App.get_running_app()
        app.root.current = 'main_menu'  # Cambiar a la pantalla del menú principal



    # Métodos para Usuarios
    def load_users(self):
        self.users_container.clear_widgets()
        users = self.trip.users
        for user in users:
            user_label = Label(text=user.name)
            self.users_container.add_widget(user_label)
            
    def show_add_user_popup(self, instance):
        popup = Popup(title='Añadir Usuario', size_hint=(None, None), size=(300, 200))
        user_name_input = TextInput(multiline=False, hint_text='Nombre de Usuario')

        confirm_button = Button(text='Confirmar', size_hint=(1, None), height=40)
        cancel_button = Button(text='Cancelar', size_hint=(1, None), height=40)

        def add_new_user():
            user_name = user_name_input.text
            if user_name:
                # Llamar a la función de backend para agregar un usuario al viaje
                user = User(user_name)  # Suponiendo que tienes una clase User en tu backend
                self.trip.add_user(user)
                self.load_users()  # Actualizar la lista de usuarios después de agregar uno nuevo

        confirm_button.bind(on_release=lambda instance: (add_new_user(), popup.dismiss()))
        cancel_button.bind(on_release=popup.dismiss)

        popup.content = BoxLayout(orientation='vertical')
        popup.content.add_widget(user_name_input)

        buttons_layout = BoxLayout(size_hint=(1, None), height=40)
        buttons_layout.add_widget(confirm_button)
        buttons_layout.add_widget(cancel_button)
        popup.content.add_widget(buttons_layout)

        popup.open()
        
    def show_remove_user_popup(self, instance):
        popup = Popup(title='Eliminar Usuario', size_hint=(None, None), size=(300, 200))
        user_name_input = TextInput(multiline=False, hint_text='Nombre de Usuario')

        confirm_button = Button(text='Confirmar', size_hint=(1, None), height=40)
        cancel_button = Button(text='Cancelar', size_hint=(1, None), height=40)

        def remove_existing_user():
            user_name = user_name_input.text
            if user_name:
                # Llamar a la función de backend para eliminar un usuario del viaje
                self.trip.remove_user(user_name)
                self.load_users()  # Actualizar la lista de usuarios después de eliminar uno existente

        confirm_button.bind(on_release=lambda instance: (remove_existing_user(), popup.dismiss()))
        cancel_button.bind(on_release=popup.dismiss)

        popup.content = BoxLayout(orientation='vertical')
        popup.content.add_widget(user_name_input)

        buttons_layout = BoxLayout(size_hint=(1, None), height=40)
        buttons_layout.add_widget(confirm_button)
        buttons_layout.add_widget(cancel_button)
        popup.content.add_widget(buttons_layout)

        popup.open()      
          
      
    def show_add_transaction_popup(self, instance):
        popup = Popup(title='Añadir Transacción', size_hint=(None, None), size=(300, 200))
        description_input = TextInput(multiline=False, hint_text='Descripción')
        amount_input = TextInput(multiline=False, hint_text='Monto')
        user_input = TextInput(multiline=False, hint_text='Nombre de Usuario')

        confirm_button = Button(text='Confirmar', size_hint=(1, None), height=40)
        cancel_button = Button(text='Cancelar', size_hint=(1, None), height=40)

        def add_new_transaction():
            description = description_input.text
            amount = amount_input.text
            user_name = user_input.text
            if description and amount and user_name:
                # Llamar a la función de backend para agregar la transacción al viaje
                user = User(user_name)  # Suponiendo que tienes una clase User en tu backend
                transaction = Transaction(description, float(amount), user_name)
                self.trip.add_transaction(transaction, user)
                self.load_transactions()  # Actualizar la lista de transacciones después de agregar una nueva

        confirm_button.bind(on_release=lambda instance: (add_new_transaction(), popup.dismiss()))
        cancel_button.bind(on_release=popup.dismiss)

        popup.content = BoxLayout(orientation='vertical')
        popup.content.add_widget(description_input)
        popup.content.add_widget(amount_input)
        popup.content.add_widget(user_input)

        buttons_layout = BoxLayout(size_hint=(1, None), height=40)
        buttons_layout.add_widget(confirm_button)
        buttons_layout.add_widget(cancel_button)
        popup.content.add_widget(buttons_layout)

        popup.open()
    
    def load_transactions(self):
        self.transactions_container.clear_widgets()
        all_transactions = self.trip.get_all_transactions()
        if all_transactions:
            for transaction in all_transactions:
                transaction_label = Label(
                    text=f'Descripción: {transaction.description}, Monto: {transaction.amount}'
                )
                self.transactions_container.add_widget(transaction_label)
        else:
            no_transactions_label = Label(text='No hay transacciones para este viaje.')
            self.transactions_container.add_widget(no_transactions_label)


class EthDividerApp(App):
    def build(self):
        self.screen_manager = ScreenManager()

        welcome_screen = Screen(name='welcome_screen')
        welcome_screen.add_widget(WelcomeScreen())

        main_menu_screen = Screen(name='main_menu')
        main_menu_screen.add_widget(MainMenuScreen())

        self.screen_manager.add_widget(welcome_screen)
        self.screen_manager.add_widget(main_menu_screen)

        return self.screen_manager


if __name__ == '__main__':
    EthDividerApp().run()
