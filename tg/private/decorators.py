def to_main_on_exception(func):
    def wrapped(update, context, *args, **kwargs):
        try:
            return func(update, context, *args, **kwargs)
        except:
            pass
