#-*- encoding:utf-8 -*-
from entities import TEntity


class TEntityReader(object):
    def HasNext(self):
        return False

    def Next(self):
        return None

class TListEntitiesReader(TEntityReader):
    def __init__(self, entitiesList):
        # sort entities by start pos and length (longer goes first)
        self.Entities = sorted(entitiesList,
                              cmp=lambda first, second: cmp((first.StartPos,
                                                             -first.EndPos + first.StartPos),
                                                            ((second.StartPos,
                                                              -second.EndPos + second.StartPos))))
        self.Pos = 0

    def HasNext(self):
        return self.Pos < len(self.Entities)

    def Next(self):
        if self.Pos >= len(self.Entities):
            return None
        entity = self.Entities[self.Pos]
        self.Pos += 1
        return entity

# entities in file are supposed to be sorted by their start position
class TFileEntitiesReader(TEntityReader):
    def __init__(self, tuplesFile):
        self.TuplesFile = tuplesFile
        self.nextLine = self.TuplesFile.readline()

    def HasNext(self):
        return len(self.nextLine) > 0

    def Next(self):
        line = self.nextLine
        self.nextLine = self.TuplesFile.readline()
        type, start, end, properties = line.split("|||")
        properties = properties.strip()
        return TEntity(type, int(start), int(end), properties)

class TTextReader(object):

    def __init__(self):
        self.Pos = 0

    def ShowNext(self, chunkSize):
        return ""

    def GetPos(self):
        return self.Pos

    def Shift(self):
        pass

    def WriteToStream(self, stream, countBytes=-1):
        pass

class TFileTextReader(TTextReader):
    def __init__(self, textFile):
        self.Pos = 0
        self.TextFile = textFile
        self.Buffer = ""

    def ShowNext(self, chunkSize=-1):
        if chunkSize == -1:
            self.Buffer += self.TextFile.read()
            return self.Buffer
        deltaLen = chunkSize - len(self.Buffer)
        if deltaLen > 0:
            self.Buffer += self.TextFile.read(deltaLen)
        return self.Buffer[:chunkSize]

    def Shift(self, size=-1):
        if size == -1:
            readBytes = len(self.TextFile.read())
            self.Pos += readBytes + len(self.Buffer)
            self.Buffer = ""
        else:
            deltaLen = size - len(self.Buffer)
            if deltaLen > 0:
                readBytes = len(self.TextFile.read(deltaLen))
            self.Pos += readBytes + min(size, len(self.Buffer))
            self.Buffer = self.Buffer[size:]


    def WriteToStream(self, stream, countBytes=-1):
        #safely read data chunk-by-chunk, making sure not uploading into memory whole Internet
        MAX_CHUNK_LEN = 1024
        if countBytes == -1:
            stream.write(self.Buffer)
            self.Pos += len(self.Buffer)
            self.Buffer = ""
            while True:
                chunk = self.TextFile.read(MAX_CHUNK_LEN)
                self.Pos += len(chunk)
                stream.write(chunk)
                if len(chunk) < MAX_CHUNK_LEN:
                    break
        else:
            fromBuffer = min(len(self.Buffer), countBytes)
            countBytes -= fromBuffer
            stream.write(self.Buffer[:fromBuffer])
            self.Buffer = self.Buffer[fromBuffer:]
            self.Pos += fromBuffer
            while countBytes:
                chunk = self.TextFile.read(min(MAX_CHUNK_LEN, countBytes))
                self.Pos += len(chunk)
                countBytes -= len(chunk)
                stream.write(chunk)
                if not chunk:
                    break



class TStringTextReader(TTextReader):
    def __init__(self, text):
        self.Pos = 0
        self.Text = text

    def ShowNext(self, chunkSize=-1):
        if chunkSize == -1:
            return self.Text[self.Pos:]
        return self.Text[self.Pos:self.Pos + chunkSize]


    def Shift(self, size=-1):
        if size == -1:
            self.Pos = len(self.Text)
        else:
            self.Pos = min(self.Pos + size, len(self.Text))


    def WriteToStream(self, stream, countBytes=-1):
        if countBytes == -1:
            stream.write(self.Text[self.Pos:])
            self.Pos = len(self.Text)
        else:
            endPos = min(len(self.Text), self.Pos + countBytes)
            stream.write(self.Text[self.Pos:endPos])
            self.Pos = endPos