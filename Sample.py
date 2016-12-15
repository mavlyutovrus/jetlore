#-*- encoding:utf-8 -*-

from decorators import DecorateString, DecorateStream
from wrappers import TAnyEntityWrapper, TLinkWrapper, TTagLinkWrapper
from entities import TEntity

wrappers = [TAnyEntityWrapper(), TLinkWrapper(), TTagLinkWrapper()]

text = """Obama visited Facebook headquarters: http://bit.ly/xyz @elversatile"""
entities = [TEntity("Entity", 14, 22, "type='company'"),
            TEntity("Entity", 0, 5, "type='person'"),
            TEntity("TagLink", 56, 67, ""),
            TEntity("Link", 37, 54, "")]



print """ string processing run """
print DecorateString(entities, text, wrappers)


print """ stream processing run """
outText = open("text.txt", "w")
outText.write(text)
outText.close()
outEnts = open("entities.txt", "w")
# sort entities by start pos and length (longer goes first)
entities = sorted(entities,
                  cmp=lambda first, second: cmp((first.StartPos,
                                                 -first.EndPos + first.StartPos),
                                                ((second.StartPos,
                                                  -second.EndPos + second.StartPos))))
for entity in entities:
    outEnts.write("%s|||%d|||%d|||%s\n" % (entity.Type, entity.StartPos, entity.EndPos, entity.Properties))
outEnts.close()
outDecorated = open("decorated.txt", "wb", buffering=10000)
decoratedTest = DecorateStream(open("entities.txt"), open("text.txt"), outDecorated, wrappers)
outDecorated.close()

decoratedTest = open("decorated.txt").read()
print decoratedTest