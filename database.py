import src.stoid
import random


class LinkDB:
    char_limit = 3
    base = len(src.stoid.CHAR_MAP)
    db = {}

    max_fail = 5

    # add_rand: Add a new link to the database with a random ID
    # Returns ID of link if successful, -X if fail
    def add_rand(self, link):
        if link in self.db.values():
            val = [key for key, value in self.db.items() if value == link]
            return val[0]
        else:
            link_id = random.randrange(pow(self.base, self.char_limit))
            fails = 0
            while self.db.get(link_id) and fails < self.max_fail:
                link_id = random.randrange(pow(self.base, self.char_limit))
                fails += 1

            # Failure can be dealt with by the managing function
            if fails >= self.max_fail:
                print("DB: Failed to add link %(link)s to database: Too many collisions!"
                      % {"link": link})
                return -1
            else:
                self.db[link_id] = link
                print("DB: Added link %(link)s with ID #%(id)d to database."
                      % {"link": link, "id": link_id})
                return link_id

    # add_with_id: Add a new link with a specific ID
    # Returns ID of link if successful, -X if fail
    def add_with_id(self, link, link_id):
        if link_id >= pow(self.base, self.char_limit) or link_id < 0:
            print("DB: Failed to add link %(link)s with ID #%(id)d to database: ID out of range!"
                  % {"link": link, "id": link_id})
            return -2

        if self.db.get(link_id):
            print("DB: Failed to add link %(link)s with ID #%(id)d to database: ID already taken!"
                  % {"link": link, "id": link_id})
            return -1

        else:
            self.db[link_id] = link
            print("DB: Added link %(link)s with ID #%(id)d to database."
                  % {"link": link, "id": link_id})
            return link_id

    # remove_by_id: Removes an item with a specific ID
    # Returns ID of link if successful, -X if fail
    def remove_by_id(self, link_id):
        if link_id >= pow(self.base, self.char_limit) or link_id < 0:
            print("DB: Failed to remove link with ID #%(id)d from database: ID out of range!"
                  % {"id": link_id})
            return -2
        if self.db.get(link_id):
            link = self.db[link_id]
            del self.db[link_id]
            print("DB: Removed link %(link)s with ID #%(id)d from database."
                  % {"link": link, "id": link_id})
            return link_id
        else:
            print("DB: Failed to remove link with ID #%(id)d from database: ID not found!"
                  % {"id": link_id})
            return -1

    # remove_by_link: Removes a specific link from the DB
    # Returns ID of link if successful, -X if fail
    def remove_by_link(self, link):
        if link in self.db.values():
            val = [key for key, value in self.db.items() if value == link]
            link_id = val[0]
            del self.db[link_id]
            print("DB: Removed link %(link)s with ID #%(id)d from database."
                  % {"link": link, "id": link_id})
            return link_id
        else:
            print("DB: Failed to remove link %(link)s from database: Link not found!"
                  % {"link": link})
            return -1

    # update_by_id: updates an ID with a new link.
    # Returns ID of link if successful, -X if fail
    def update_by_id(self, link_id, new_link):
        if link_id >= pow(self.base, self.char_limit) or link_id < 0:
            print("DB: Failed to update ID #%(id)d to new link %(link)s: ID out of range!"
                  % {"link": new_link, "id": link_id})
            return -2

        if self.db.get(link_id) and new_link not in self.db.values():
            self.db[link_id] = new_link
            print("DB: Updated ID #%(id)d to new link %(link)s."
                  % {"link": new_link, "id": link_id})
            return link_id
        elif new_link in self.db.values():
            val = [key for key, value in self.db.items() if value == new_link]
            print("DB: Failed to update ID #%(id)d to new link %(link)s: Link already in database!"
                  % {"link": new_link, "id": link_id})
            return val[0]
        else:
            print("DB: Failed to update ID #%(id)d to new link %(link)s: ID not found!"
                  % {"link": new_link, "id": link_id})
            return -1

    def update_by_link(self, link, new_id):
        if new_id >= pow(self.base, self.char_limit) or new_id < 0:
            print("DB: Failed to update link %(link)s to new ID #%(id)d: ID out of range!"
                  % {"link": link, "id": new_id})
            return -2
        elif self.db.get(new_id):
            print("DB: Failed to update link %(link)s with ID #%(id)d to database: ID already taken!"
                  % {"link": link, "id": new_id})
            return -1
        elif link in self.db.values():
            val = [key for key, value in self.db.items() if value == link]
            self.db[new_id] = link
            ec = self.remove_by_id(val[0]) #TODO: Doublecheck error checking here
            print("DB: Updated link %(link)s to new ID #%(id)d."
                  % {"link": link, "id": new_id})
            return new_id
        else:
            print("DB: Failed to update link %(link)s with ID #%(id)d to database: Link not found!"
                  % {"link": link, "id": new_id})
            return -3


    # get_link_by_id: Returns the DB entry for a given ID
    # returns the link, or None if no matching ID is found.
    def get_link_by_id(self, link_id):
        return self.db.get(link_id)

    # get_id_by_link: Returns the ID for a given link
    # returns the ID, or None if no matching link is found.
    def get_id_by_link(self, link):
        if link in self.db.values():
            val = [key for key, value in self.db.items() if value == link]
            return val[0]
        else:
            return None
