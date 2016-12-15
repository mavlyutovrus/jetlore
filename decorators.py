#-*- encoding:utf-8 -*-
from entities import TEntity


"""
  textReader - TTextReader
  entitiesReader - TEntityReader
  outputWriter - writeable object
  wrappers - list of wrappers to use
"""

def IDecorate(textReader, entitiesReader, outputWriter, wrappers):
    wrappers = {wrapper.GetType(): wrapper for wrapper in wrappers}
    import heapq
    closeTags = []
    def flushCloseTags(upToPos=-1):
        while closeTags and (upToPos == -1 or closeTags[0][0] <= upToPos):
            closeTagPos, _, closeTag = heapq.heappop(closeTags)
            undecChunkLen = closeTagPos - textReader.GetPos()
            textReader.WriteToStream(outputWriter, undecChunkLen)
            outputWriter.write(closeTag)
    entityIndex = 0
    while entitiesReader.HasNext():
        nextEntity = entitiesReader.Next()
        #skip entities that are not supposed to be enclosed with tags
        if not nextEntity.Type in wrappers:
            continue
        flushCloseTags(nextEntity.StartPos)
        undecChunkLen = nextEntity.StartPos - textReader.GetPos()
        textReader.WriteToStream(outputWriter, undecChunkLen)
        entityText = textReader.ShowNext(nextEntity.EndPos - nextEntity.StartPos)
        openTag, closeTag = wrappers[nextEntity.Type].GetOpenCloseTags(entityText, nextEntity.Type, nextEntity.Properties)
        outputWriter.write(openTag)
        entityIndex +=1
        #we use entity index to return close tags in reverse order "<obj1><obj2>blabla<obj2><obj1>"
        heapq.heappush(closeTags, (nextEntity.EndPos, -entityIndex, closeTag))
    flushCloseTags()
    textReader.WriteToStream(outputWriter)


def DecorateString(entitiesList, textString, wrappers):
    import StringIO
    from readers import TStringTextReader, TListEntitiesReader
    text = TStringTextReader(textString)
    entities = TListEntitiesReader(entitiesList)
    output = StringIO.StringIO()
    IDecorate(text, entities, output, wrappers)
    return output.getvalue()


#entitiesStream: sorted by start position and length (longer goes before)
def DecorateStream(entitiesStream, textStream, outputStream, wrappers):
    import StringIO
    from readers import TFileTextReader, TFileEntitiesReader
    text = TFileTextReader(textStream)
    entities = TFileEntitiesReader(entitiesStream)
    IDecorate(text, entities, outputStream, wrappers)

























