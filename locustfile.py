from datetime import datetime

from locust import HttpUser, task, between
from faker import Faker

faker = Faker()

class APIUser(HttpUser):
    wait_time = between(1, 2.5)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def register_user(self):
        first_name = faker.first_name()
        last_name = faker.last_name()
        email = first_name.lower() + "." + last_name.lower() + "." + faker.uuid4() + "@example.com"
        password = faker.password()
        data = {
            "email": email,
            "password": password,
            "name": {
                "firstName": first_name,
                "lastName": last_name
            }
        }
        response = self.client.post("/api/authentication/register", json=data)
        return response, email, password

    def login_user(self, email, password):
        login_data = {
            "username": email,
            "password": password
        }
        response = self.client.post("/api/authentication/login", json=login_data)
        return response

    def create_smart_meter(self, access_token):
        smart_meter_data = {
            "name": faker.word()
        }
        response = self.client.post("/api/smartMeters", json=smart_meter_data,
                                    headers={"Authorization": f"Bearer {access_token}"})
        return response

    @task
    def register(self):
        response, email, _ = self.register_user()
        if response.status_code != 200:
            print(f"User {email} registration failed")
            print(response.text)

    @task
    def login(self):
        response, email, password = self.register_user()
        if response.status_code != 200:
            print(f"User {email} registration failed")
            print(response.text)
            return

        response = self.login_user(email, password)
        if response.status_code != 200:
            print(f"User {email} login failed")
            print(response.text)

    @task
    def refresh(self):
        response, email, password = self.register_user()
        if response.status_code != 200:
            print(f"User {email} registration failed")
            print(response.text)
            return

        response = self.login_user(email, password)
        if response.status_code != 200:
            print(f"User {email} login failed")
            print(response.text)
            return

        token = response.json()
        refresh_data = {
            "accessToken": token["accessToken"],
            "refreshToken": token["refreshToken"]
        }
        response = self.client.post("/api/authentication/refresh", json=refresh_data)
        if response.status_code != 200:
            print(f"User {email} refresh failed")
            print(response.text)

    @task
    def logout(self):
        response, email, password = self.register_user()
        if response.status_code != 200:
            print(f"User {email} registration failed")
            print(response.text)
            return

        response = self.login_user(email, password)
        if response.status_code != 200:
            print(f"User {email} login failed")
            print(response.text)
            return

        token = response.json()
        logout_data = {
            "accessToken": token["accessToken"],
            "refreshToken": token["refreshToken"]
        }
        response = self.client.post("/api/authentication/logout", json=logout_data)
        if response.status_code != 200:
            print(f"User {email} logout failed")
            print(response.text)

    @task
    def add_smart_meter(self):
        response, email, password = self.register_user()
        if response.status_code != 200:
            print(f"User {email} registration failed")
            print(response.text)
            return

        response = self.login_user(email, password)
        if response.status_code != 200:
            print(f"User {email} login failed")
            print(response.text)
            return

        token = response.json()
        access_token = token["accessToken"]

        response = self.create_smart_meter(access_token)
        if response.status_code != 201:
            print(f"Add smart meter failed")
            print(response.text)

    @task
    def get_smart_meters(self):
        response, email, password = self.register_user()
        if response.status_code != 200:
            print(f"User {email} registration failed")
            print(response.text)
            return

        response = self.login_user(email, password)
        if response.status_code != 200:
            print(f"User {email} login failed")
            print(response.text)
            return

        token = response.json()
        access_token = token["accessToken"]

        for _ in range(3):
            self.create_smart_meter(access_token)

        response = self.client.get("/api/smartMeters", headers={"Authorization": f"Bearer {access_token}"})
        if response.status_code != 200:
            print("Get smart meters failed")
            print(response.text)

    @task
    def get_smart_meter_by_id(self):
        response, email, password = self.register_user()
        if response.status_code != 200:
            print(f"User {email} registration failed")
            print(response.text)
            return

        response = self.login_user(email, password)
        if response.status_code != 200:
            print(f"User {email} login failed")
            print(response.text)
            return

        token = response.json()
        access_token = token["accessToken"]

        response = self.create_smart_meter(access_token)
        if response.status_code != 201:
            print("Create smart meter failed")
            print(response.text)
            return

        smart_meter_id = response.headers["Location"].split("/")[-1]
        response = self.client.get(f"/api/smartMeters/{smart_meter_id}",
                                   headers={"Authorization": f"Bearer {access_token}"})
        if response.status_code != 200:
            print("Get smart meter by id failed")
            print(response.text)

    @task
    def update_smart_meter(self):
        response, email, password = self.register_user()
        if response.status_code != 200:
            print(f"User {email} registration failed")
            print(response.text)
            return

        response = self.login_user(email, password)
        if response.status_code != 200:
            print(f"User {email} login failed")
            print(response.text)
            return

        token = response.json()
        access_token = token["accessToken"]

        response = self.create_smart_meter(access_token)
        if response.status_code != 201:
            print("Create smart meter failed")
            print(response.text)
            return

        smart_meter_id = response.headers["Location"].split("/")[-1]
        update_data = {
            "id": smart_meter_id,
            "name": faker.word()
        }
        response = self.client.put(f"/api/smartMeters/{smart_meter_id}", json=update_data,
                                   headers={"Authorization": f"Bearer {access_token}"})
        if response.status_code != 200:
            print("Update smart meter failed")
            print(response.text)

    @task
    def add_metadata(self):
        response, email, password = self.register_user()
        if response.status_code != 200:
            print(f"User {email} registration failed")
            print(response.text)
            return

        response = self.login_user(email, password)
        if response.status_code != 200:
            print(f"User {email} login failed")
            print(response.text)
            return

        token = response.json()
        access_token = token["accessToken"]

        response = self.create_smart_meter(access_token)
        if response.status_code != 201:
            print("Create smart meter failed")
            print(response.text)
            return

        smart_meter_id = response.headers["Location"].split("/")[-1]
        metadata_data = {
            "validFrom": datetime.utcnow().isoformat() + 'Z',
            "location": {
                "streetName": faker.street_name(),
                "city": faker.city(),
                "state": faker.state(),
                "country": faker.country(),
                "continent": faker.random_int(0, 6)
            },
            "householdSize": faker.random_int(1, 10)
        }

        response = self.client.post(f"/api/smartMeters/{smart_meter_id}/metadata", json=metadata_data,
                                    headers={"Authorization": f"Bearer {access_token}"})
        if response.status_code != 200:
            print("Add metadata failed")
            print(response.text)