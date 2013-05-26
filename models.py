from kunjika import cb
class User():

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self, email):
        try:
            document = cb.get(email)[2]
            return unicode(document['email'])
        except:
            return None

#    def __repr__(self):
#        return '<User %r>' % (self.fname)
