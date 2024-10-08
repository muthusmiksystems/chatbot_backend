
class DatabaseRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'users':
            return 'default'  # MySQL
        elif model._meta.app_label == 'bots':
            return 'mongo'  # mongo
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'users':
            return 'default'
        elif model._meta.app_label == 'bots':
            return 'mongo'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == obj2._meta.app_label:
            return True
        return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'users':
            return db == 'default'
        elif app_label == 'bots':
            return db == 'mongo'
        return None
