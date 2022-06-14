import src.stoid
import random


class LinkDB:
    char_limit = 5
    base = len(src.stoid.CHAR_MAP)
    db = {}

    max_fail = 5

    # add_rand: Add a new link to the database with a random ID
    # Returns ID of link if successful, -1 if fail
    def add_rand(self, link):
        if link in self.db.values():
            val = [key for key, value in self.db if value == link]
            return val[0]
        else:
            link_id = random.randrange(pow(self.base, self.char_limit))
            fails = 0
            while self.db.get(link_id) and fails < self.max_fail:
                link_id = random.randrange(pow(self.base, self.char_limit))
                fails += 1

            # Failure can be dealt with by the managing function
            if fails >= self.max_fail:
                return -1
            else:
                self.db[link_id] = link
                print("Added link %s with ID #%d to database." % (link, link_id))
                return link_id

    # add_with_id: Add a new link with a specific ID
    # Returns ID of link if successful, -1 if fail
    def add_with_id(self, link, link_id):
        if self.db.get(link_id):
            return -1
        else:
            self.db[link_id] = link
            print("Added link %s with ID #%d to database." % (link, link_id))
            return link_id

    # remove_by_id: Removes an item with a specific ID
    # Returns ID of link if successful, -1 if fail
    def remove_by_id(self, link_id):
        if self.db.get(link_id):
            link = self.db[link_id]
            del self.db[link_id]
            print("Removed link %s with ID #%d from database." % (link, link_id))
            return link_id
        else:
            return -1

    # remove_by_link: Removes a specific link from the DB
    # Returns ID of link if successful, -1 if fail
    def remove_by_link(self, link):
        if link in self.db.values():
            val = [key for key, value in self.db if value == link]
            link_id = val[0]
            del self.db[link_id]
            print("Removed link %s with ID #%d from database." % (link, link_id))
            return link_id
        else:
            return -1

    # update_by_id: updates an ID with a new link.
    # Returns ID of link if successful, -1 if fail
    def update_by_id(self, link_id, new_link):
        if self.db.get(link_id) and new_link not in self.db.values():
            self.db[link_id] = new_link
            print("Updated ID #%d to new link %s." % (link_id, new_link))
            return link_id
        elif new_link in self.db.values():
            val = [key for key, value in self.db if value == new_link]
            return val[0]
        else:
            return -1

    # get_link_by_id: Returns the DB entry for a given ID
    # returns the link, or None if no matching ID is found.
    def get_link_by_id(self, link_id):
        return self.db.get(link_id)

    # get_id_by_link: Returns the ID for a given link
    # returns the ID, or None if no matching link is found.
    def get_id_by_link(self, link):
        if link in self.db.values():
            val = [key for key, value in self.db if value == link]
            return val[0]
        else:
            return None
