# Copyright (c) 2010, Ryan Bourgeois <bluedragonx@gmail.com>
# All rights reserved.
#
# This software is licensed under the GNU General Public License v2.0.
# A copy of the license should have been included with this file but
# is available online at http://www.gnu.org/licenses/gpl-2.0.html.
# This software is provided "as is" and any and all express or implied
# warranties are disclaimed, including, but not limited to, the implied
# warranties of title, merchantability, against infringement, and fitness
# for a particular purpose.

from couchdbkit import Document, StringProperty, SchemaListProperty
import bcrypt

def hashpw(password, salt=None):
    """
    Hash a password using the optional salt.  If salt is not specified one
    will be generated.  The hash, which includes the salt, is returned.
    :param password: The password to hash.
    :param salt: The optional salt to use.
    :return: The hashed password.
    """
    if salt is None:
        salt = bcrypt.gensalt()
    return unicode(bcrypt.hashpw(password, salt))

def hashcmp(hash, password):
    """
    Compare a hash to an un-hashed password.  Returns True if they match
    or false otherwise.
    :param hash A password hash generated by hashpw().
    :param password An unhashed password to compare against.
    :return: True if the password matches the hash, False if it does not.
    """
    salt = hash[:29]
    return hash == hashpw(password, salt)

class Permission(Document):
    """
    Permission document.  Permissions belong to groups in a many-to-many relationship.
    """
    name = StringProperty(required=True)

class Group(Document):
    """
    Group document.  Groups are assigned to users in a many-to-many relationship.
    """
    name = StringProperty(required=True)
    permissions = SchemaListProperty(Permission)

class User(Document):
    """
    User document.
    """
    username = StringProperty(required=True)
    password = StringProperty()
    groups = SchemaListProperty(Group)

    @staticmethod
    def create(username, password, groups=[]):
        """
        Convenience method for creating a new user.
        :param username: The username of the new user.
        :param password: The password of the new user.
        :param groups: The groups to assign to the new user.
        :return: The new user document.
        """
        hash = hashpw(password)
        return User(username=username, password=hash, groups=groups)

    def authenticate(self, password):
        """
        Authenticate the user against a plaintext password.
        :param password: The plaintext password to authenticate the user with.
        :return: True if authentication is successful, False otherwise.
        """
        return hashcmp(self.password, password)

    def set_password(self, password):
        """
        Set the password.  Hashed the password before setting.
        :param password: The password to set in plaintext.
        """
        self.password = hashpw(password)

def init_model(database):
    """
    Initialize the model.  Associates the given database with each of the documents.
    :param database: The database to initialize the model with.
    """
    User.set_db(database)
    Group.set_db(database)
    Permission.set_db(database)

