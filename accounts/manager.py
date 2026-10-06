from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, phone_number, email, password, first_name, last_name, state,
                    city, address, zip_code):   # this function creates user
        if not phone_number:   # raises error whenever a phone number is not inserted
            raise ValueError("User must have phone number")
        if not email:   # raises error whenever an email is not inserted
            raise ValueError("User must have email")
        if not password:   # raises error whenever a password is not inserted
            raise ValueError("User must have password")
        if not first_name:   # raises error whenever a first_name is not inserted
            raise ValueError("User must have first name")
        if not last_name:   # raises error whenever a last_name is not inserted
            raise ValueError("User must have last name")
        if not state:   # raises error whenever a state is not inserted
            raise ValueError("User must have state")
        if not city:   # raises error whenever a city is not inserted
            raise ValueError("User must have city")
        if not address:   # raises error whenever an address is not inserted
            raise ValueError("User must have address")
        if not zip_code:   # raises error whenever a zip_code is not inserted
            raise ValueError("User must have zip_code")
        user = self.model(
            phone_number = phone_number,
            email = email,
            first_name = first_name,
            last_name = last_name,
            state=state,
            city = city,
            address=address,
            zip_code = zip_code,
        )   # creates user in model with given information
        user.set_password(password)   # sets password using set_password feature of abstract base user
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, email, password, first_name, last_name, state,
                         city, address, zip_code):   # this function creates superuser
        user = self.create_user(phone_number, email, password, first_name, last_name, state, city, address, zip_code)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)   # saving created superuser
        return user
