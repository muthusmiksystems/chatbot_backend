class DatabaseRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'bots':
            return 'mongo'
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'bots':
            return 'mongo'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        # Allow relations if both objects are in the same database
        db_set = {'default', 'mongo'}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Ensure migrations for 'users' app occur in the default database
        if app_label == 'users':
            return db == 'default'
        # Ensure migrations for 'bots' app occur in the mongo database
        if app_label == 'bots':
            return db == 'mongo'
        # Allow migrations for default Django apps in the default database
        if app_label in {'contenttypes', 'auth', 'admin', 'sessions'}:
            return db == 'default'
        return None
