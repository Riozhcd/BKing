import gzip

class DocIndex:
    '''
    Handle one document into a dict with position
    '''
    index = {}
    def __init__(self):
        self.index = dict()

    def push(self, word, pos):
        if word in self.index:
            self.index[word].append(pos)
        else:
            self.index[word] = [pos]

    def dump_gzip(self, filename):
        """
        dump index to file with zip
        :param filename:
        :return:
        """
        f = gzip.open(filename, "wb")
        for i in self.index:
            content = i + " "
            for v in self.index[i]:
                content += str(v) + ","
            content = content[:-1] + "\n"
            f.write(bytes(content, "utf8"))
        f.close()
        
    def dump(self, filename):
        """
        dump index to plain text file
        :param filename:
        :return:
        """
        f = open(filename, "w")
        for i in self.index:
            content = i + " "
            for v in self.index[i]:
                content += str(v) + ","
            content = content[:-1] + "\n"
            f.write(content)
        f.close()
    @staticmethod
    def read_gzip(filename):
        """
        read index file with gzip to partial index
        :param filename:
        :return:
        """
        f = gzip.open(filename, "rb")
        lines = f.readlines()
        pi = PartialIndex()
        for line in lines:
            content = line.decode("utf8")
            content = content.split(" ")
            val = content[1].split(',')
            for v in val:
                pi.push(content[0], int(v))
        f.close()
        return pi

    @staticmethod
    def read(filename):
        """
        read plain text index file to partial index
        :param filename:
        :return:
        """
        f = open(filename, "r")
        lines = f.readlines()
        pi = PartialIndex()
        for line in lines:
            content = line
            content = content.split(" ")
            val = content[1].split(',')
            for v in val:
                pi.push(content[0], int(v))
        f.close()
        return pi