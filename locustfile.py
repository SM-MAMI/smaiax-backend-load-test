from datetime import datetime
from locust import HttpUser, task, between
from faker import Faker

faker = Faker()

class APIUser(HttpUser):
    wait_time = between(1, 2.5)
    email = None
    password = None
    access_token = None
    refresh_token = None

    def on_start(self):
        """Runs once per user at the start of the test."""
        # Register and login the user
        response, self.email, self.password = self.register_user()
        if response.status_code == 200:
            login_response = self.login_user(self.email, self.password)
            if login_response.status_code == 200:
                self.access_token = login_response.json().get("accessToken")
                self.refresh_token = login_response.json().get("refreshToken")
            else:
                print(f"Login failed for user {self.email}: {login_response.text}")
                self.access_token = None
                self.refresh_token = None
        else:
            print(f"Registration failed for user {self.email}: {response.text}")
            self.access_token = None
            self.refresh_token = None

    def on_stop(self):
        """Runs once per user at the end of the test."""
        if self.access_token:
            self.logout_user()

    def register_user(self):
        first_name = faker.first_name()
        last_name = faker.last_name()
        email = f"{first_name.lower()}.{last_name.lower()}.{faker.uuid4()}@example.com"
        password = faker.password()
        data = {
            "email": email,
            "password": password,
            "name": {
                "firstName": first_name,
                "lastName": last_name
            }
        }
        response = self.client.post("/api/authentication/register", json=data, name="register")
        return response, email, password

    def login_user(self, email, password):
        login_data = {
            "username": email,
            "password": password
        }
        return self.client.post("/api/authentication/login", json=login_data, name="login")

    def logout_user(self):
        logout_data = {
            "accessToken": self.access_token,
            "refreshToken": self.refresh_token
        }
        response = self.client.post("/api/authentication/logout", json=logout_data, name="logout")
        if response.status_code != 200:
            print(f"Logout failed for user {self.email}: {response.text}")

    def create_smart_meter(self):
        smart_meter_data = {
            "name": faker.word()
        }
        return self.client.post("/api/smartMeters", json=smart_meter_data,
                                headers={"Authorization": f"Bearer {self.access_token}"}, name="add_smart_meter")

    @task
    def add_smart_meter(self):
        if self.access_token:
            response = self.create_smart_meter()
            if response.status_code != 201:
                print("Add smart meter failed")
                print(response.text)

    @task
    def get_smart_meters(self):
        if self.access_token:
            for _ in range(3):
                self.create_smart_meter()
            response = self.client.get("/api/smartMeters",
                                       headers={"Authorization": f"Bearer {self.access_token}"}, name="get_smart_meters")
            if response.status_code != 200:
                print("Get smart meters failed")
                print(response.text)

    @task
    def get_smart_meter_by_id(self):
        if self.access_token:
            response = self.create_smart_meter()
            if response.status_code == 201:
                smart_meter_id = response.headers["Location"].split("/")[-1]
                response = self.client.get(f"/api/smartMeters/{smart_meter_id}",
                                           headers={"Authorization": f"Bearer {self.access_token}"}, name="get_smart_meter_by_id")
                if response.status_code != 200:
                    print("Get smart meter by id failed")
                    print(response.text)

    @task
    def update_smart_meter(self):
        if self.access_token:
            response = self.create_smart_meter()
            if response.status_code == 201:
                smart_meter_id = response.headers["Location"].split("/")[-1]
                update_data = {
                    "id": smart_meter_id,
                    "name": faker.word()
                }
                response = self.client.put(f"/api/smartMeters/{smart_meter_id}", json=update_data,
                                           headers={"Authorization": f"Bearer {self.access_token}"}, name="update_smart_meter")
                if response.status_code != 200:
                    print("Update smart meter failed")
                    print(response.text)

    @task
    def add_metadata(self):
        if self.access_token:
            response = self.create_smart_meter()
            if response.status_code == 201:
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
                                            headers={"Authorization": f"Bearer {self.access_token}"}, name="add_metadata")
                if response.status_code != 200:
                    print("Add metadata failed")
                    print(response.text)