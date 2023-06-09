
class HandleInstance:
    def __init__(self, instance):
        self.instance = instance

    def __enter__(self):
        HandlePriority.add_instance(self.instance)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        HandlePriority.remove_instance(self.instance)

class HandlePriority:
    def __init__(self):
        if not hasattr(HandlePriority, "_first_init"):
            HandlePriority._first_init = True
            self.instances = []

    @staticmethod
    def add_instance(instance):
        print("add_instance")
        handle_priority = HandlePriority()
        handle_priority.instances.append(instance)

    @staticmethod
    def remove_instance(instance):
        print("remove_instance")
        handle_priority = HandlePriority()
        handle_priority.instances.remove(instance)

    def handle_instance(self, packet_event):
        for instance in self.instances:
            if instance.handle(packet_event):
                return True
        return False

    def notify_instance_offline(self):
        for instance in self.instances:
            instance.offline()

    def __new__(cls, *args, **kwargs):
        if not hasattr(HandlePriority, "_instance"):
            HandlePriority._instance = object.__new__(cls)
        return HandlePriority._instance

