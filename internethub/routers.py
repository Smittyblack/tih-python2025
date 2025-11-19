class GameRouter:
    def db_for_read(self, model, **hints):
        print(f"db_for_read: app_label={model._meta.app_label}, model_name={model._meta.model_name}")
        if model._meta.app_label in ['auth', 'contenttypes']:
            print("Routing to default")
            return 'default'
        if model._meta.app_label == 'spircre':
            print("Routing to game_scores")
            return 'game_scores'
        print("Routing to default (default case)")
        return 'default'

    def db_for_write(self, model, **hints):
        print(f"db_for_write: app_label={model._meta.app_label}, model_name={model._meta.model_name}")
        if model._meta.app_label in ['auth', 'contenttypes']:
            print("Routing to default")
            return 'default'
        if model._meta.app_label == 'spircre':
            print("Routing to game_scores")
            return 'game_scores'
        print("Routing to default (default case)")
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        app_label1 = obj1._meta.app_label
        app_label2 = obj2._meta.app_label

        # Allow relations within the same app
        if app_label1 == app_label2:
            return True

        # Allow relations between 'auth' or 'contenttypes' and any app in 'default' database
        if app_label1 in ['auth', 'contenttypes'] and app_label2 not in ['spircre']:
            return True
        if app_label2 in ['auth', 'contenttypes'] and app_label1 not in ['spircre']:
            return True

        # Allow relations between 'spircre' and 'auth' or 'contenttypes'
        if (app_label1 == 'spircre' and app_label2 in ['auth', 'contenttypes']) or \
                (app_label2 == 'spircre' and app_label1 in ['auth', 'contenttypes']):
            return True

        return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == 'game_scores':
            result = app_label == 'spircre'
            return result
        if db == 'default':
            result = app_label != 'spircre'
            return result
        return False