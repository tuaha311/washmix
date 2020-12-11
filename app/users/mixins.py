class ProxyUserInfoMixin:
    #
    # user proxy fields
    #
    @property
    def email(self):
        return self.user.email

    @property
    def first_name(self):
        return self.user.first_name

    @first_name.setter
    def first_name(self, value: str):
        self.user.first_name = value
        self.user.save()

    @property
    def last_name(self):
        return self.user.last_name

    @last_name.setter
    def last_name(self, value: str):
        self.user.last_name = value
        self.user.save()

    #
    # properties
    #
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
