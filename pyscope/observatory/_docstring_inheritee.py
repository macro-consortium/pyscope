from abc import ABCMeta

class _DocstringInheritee(ABCMeta):
    def __new__(mcls, classname, bases, cls_dict):
        cls = super().__new__(mcls, classname, bases, cls_dict)
        for name, member in cls_dict.items():
            if not getattr(member, '__doc__'):
                try: member.__doc__ = getattr(bases[-1], name).__doc__
                except AttributeError: pass
        return cls