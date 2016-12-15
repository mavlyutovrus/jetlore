#-*- encoding:utf-8 -*-

from entities import TEntity
from decorators import DecorateString, DecorateStream
from wrappers import TUnitTestWrapper



def GenTestCase(textLen=20, maxOpenTags=10):
    wrapper = TUnitTestWrapper()
    import random
    def genChunk():
        return "".join(["abcd"[random.randint(0,3)] for _ in xrange(random.randint(0, 4))])

    entities = []
    decorated = ""
    text = ""
    openTags = []
    entId = 0
    seen_spans = set()
    while True:
        newChunk = genChunk()
        decorated += newChunk
        text += newChunk
        isOpenTag = 1
        if len(openTags) > maxOpenTags or len(text) > textLen or random.randint(0, 10) < 4:
            isOpenTag = 0
        if (not isOpenTag and not openTags):
            if len(text) > textLen:
                break
            isOpenTag = 1
        if isOpenTag:
            entId += 1
            openTags += [(len(text), str(entId))]
            decorated += wrapper.GetOpenCloseTags("", "Dummy", str(entId))[0]
        else:
            #allow overlapping tags: "<a><b>asdasf</a><b/>
            #selected = random.randint(0, len(openTags) - 1)
            selected = len(openTags) - 1
            entStart, ID = openTags[selected]
            if (entStart, len(text)) in seen_spans: # do not allow tags with same span, since there is no way to distinguish between "<b><a></a></b>" and <a><b></b></a>
                text += "a"
                decorated += "a"
            if  entStart == len(text): # do not allow empty spans, since there is no way to distinguish between "<b>asdaf</b><a></a>" and "<b>asdaf<a></a></b>"
                text += "a"
                decorated += "a"
            openTags = openTags[:selected] + openTags[selected + 1:]
            seen_spans.add((entStart, len(text)))
            entities += [TEntity("Dummy", entStart, len(text), ID)]
            decorated += wrapper.GetOpenCloseTags("", "Dummy", ID)[1]
    return text, entities, decorated




wrappers = [TUnitTestWrapper()]

print """ string processing """
cases = 0
totalCases = 1000
for _ in xrange(totalCases):
    cases += 1
    text, entities, decorated = GenTestCase(textLen=20, maxOpenTags=10)
    decoratedTest = DecorateString(entities, text, wrappers)
    if decoratedTest != decorated:
        print "FAIL"
        print text
        print entities
        print "answer:", decorated
        print "result:", decoratedTest
        exit(1)
    if cases % 100 == 0:
        print "Successfully processed", cases, "/", totalCases
print "Done!"


""" stream processing """
cases = 0
totalCases = 100
for _ in xrange(totalCases):
    cases += 1
    text, entities, decorated = GenTestCase(textLen=2000000, maxOpenTags=10) #2Mb
    print "..generated", "text size [MB]:", len(text) / 1000000, "decorated len [MB]:", len(decorated) / 1000000
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
    print "..start"
    decoratedTest = DecorateStream(open("entities.txt"), open("text.txt"), outDecorated, wrappers)
    outDecorated.close()
    print "..done"

    decoratedTest = open("decorated.txt").read()

    if decoratedTest != decorated:
        print "FAIL"
        print text
        print entities
        print "answer:", decorated[:50], ".."
        print "result:", decoratedTest[:50], ".."
        exit(1)
    if cases % 1 == 0:
        print "Successfully processed", cases, "/", totalCases
print "Done!"




