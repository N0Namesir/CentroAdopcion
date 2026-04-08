class Dog:
    def __init__(self, dog_id, name, age, breed, adopted=False, photo=None):
        self.id      = dog_id
        self.name    = name
        self.age     = age
        self.breed   = breed
        self.adopted = adopted
        self.photo   = photo  # Nombre de archivo, ej: "42_firulais.jpg"

    @property
    def photo_url(self):
        """URL lista para usar en <img src="">. Devuelve None si no hay foto."""
        if self.photo:
            return f"/static/uploads/dogs/{self.photo}"
        return None

class Adopter:
    def __init__(self, adopter_id, name, lastName, address, id_card=None):
        self.adopter_id = adopter_id  # FK → Person.id
        self.name       = name
        self.lastName   = lastName
        self.address    = address
        self.id_card    = id_card