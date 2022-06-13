import src.stoid
import random


class LinkDB:
    char_limit = 5
    base = len(src.stoid.CHAR_MAP)
    db = {}

    max_fail = 5

    # add_rand: Add a new link to the database with a random ID
    # Returns ID if successful, -1 if fail
    def add_rand(self, link):
        if link in self.db.values():
            val = [key for key, value in self.db if value == link]
            return val[0]
        else:
            new_id = random.randrange(pow(self.base, self.char_limit))
            fails = 0
            while self.db[new_id] and fails < self.max_fail:
                new_id = random.randrange(pow(self.base, self.char_limit))
                fails += 1

            # Failure can be dealt with by the managing function
            if fails >= self.max_fail:
                return -1
            else:
                self.db[new_id] = link
                return new_id

    # add_with_id: Add a new link with a specific ID
    # Returns ID if successful, -1 if fail
    def add_with_id(self, link, link_id):
        if self.db[link_id]:
            return -1
        else:
            self.db[link_id] = link
            return link_id

    # remove_by_id: Removes an item with a specific ID
    # Returns ID if successful, -1 if fail
    def remove_by_id(self, link_id):
        if self.db[link_id]:
            del self.db[link_id]
            return link_id
        else:
            return -1

    def remove_by_link(self, link):
        if link in self.db.values():
            val = [key for key, value in self.db if value == link]
            link_id = val[0]
            del self.db[link_id]
            return link_id
        else:
            return -1

    def update_by_id(self, link_id, new_link):
        if self.db[link_id] and new_link not in self.db.values():
            self.db[link_id] = new_link
            return link_id
        elif new_link in self.db.values():
            val = [key for key, value in self.db if value == new_link]
            return val[0]
        else:
            return -1

    def get_link_by_id(self, link_id):
        return self.db[link_id]

    def get_id_by_link(self, link):
        if link in self.db.values():
            val = [key for key, value in self.db if value == new_link]
            return val[0]
        else:
            return None
