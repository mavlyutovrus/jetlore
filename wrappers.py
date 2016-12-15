#-*- encoding:utf-8 -*-

class IWrapper(object):
    def __init__(self):
        self.Type = None

    def GetType(self):
        return self.Type

    def GetOpenCloseTags(self, entityText, entityType, properties=""):
        return "<open>", "<close>"

class TUnitTestWrapper(IWrapper):
    def __init__(self):
        self.Type = "Dummy"

    def GetOpenCloseTags(self, entityText, entityType, properties=""):
        return "<%s id='%s'>" % (str(entityType), properties), "</%s id='%s'>" % (str(entityType), properties)


class TAnyEntityWrapper(IWrapper):
    def __init__(self):
        self.Type = "Entity"

    def GetOpenCloseTags(self, entityText, entityType, properties=""):
        return (properties and "<strong %s>" % (properties) or "<strong>", "</strong>")

class TLinkWrapper(IWrapper):
    def __init__(self):
        self.Type = "Link"

    def GetOpenCloseTags(self, entityText, entityType, properties=""):
        return "<a href='%s'>" % (entityText), "</a>"

class TTagLinkWrapper(IWrapper):
    def __init__(self):
        self.Type = "TagLink"

    def GetOpenCloseTags(self, entityText, entityType, properties=""):
        return "<a href='https://twitter.com/%s' target='_blank'>" % (entityText), "</a>"
