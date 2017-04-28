from HTMLParser import HTMLParser
from htmlentitydefs import name2codepointa


class Tag():
    name = ''
    text = ''
    first_child = 0
    parent = 0
    next_sibling = 0
    closed = 0
    depth = 0

    def get_tag_info_str(self):
        c, p, s = 'none', 'none', 'none'
        if self.first_child != 0:
            c = self.first_child.name
        if self.parent != 0:
            p = self.parent.name
        if self.next_sibling != 0:
            s = self.next_sibling.name
        return "name = {}, text = {}\nParent = {}, First Child = {}, Next Sibling = {}\nClosed = {}, Depth = {}\n".format(self.name, self.text, p, c, s, self.closed, self.depth)


class MyHTMLParser(HTMLParser):
    tag_list = []
    depth = 0
    previous_tag = 'none'
    mode = 'silent'

    def handle_starttag(self, tag, attrs):
        if self.mode != 'silent':
            print "Start tag:", tag
            for attr in attrs:
                print "     attr:", attr
        self.depth = self.depth + 1
        t = Tag()
        t.name = tag
        t.depth = self.depth
        if self.previous_tag == 'start':
            # current tag is a first child of the last tag
            t.parent = self.tag_list[len(self.tag_list)-1]
            self.tag_list[len(self.tag_list)-1].first_child = t
        elif self.previous_tag == 'end':
            # current tag is next sibling of the last tag

            for x in reversed(self.tag_list):
                if x.depth == self.depth:
                    x.next_sibling = t
                    if t.parent == 0:
                        t.parent = x.parent
                    break
        elif self.previous_tag == 'startend':
            # current tag is the next sibling of the previous tag
            t.parent = self.tag_list[len(self.tag_list)-1].parent
            self.tag_list[len(self.tag_list)-1].next_sibling = t

        self.tag_list.append(t)
        self.previous_tag = 'start'

    def handle_endtag(self, tag):
        if self.mode != 'silent':
            print "End tag  :", tag
        for x in reversed(self.tag_list):
            if x.name == tag and x.closed == 0:
                x.closed = 1
                break
        self.depth = self.depth - 1
        self.previous_tag = 'end'

    def handle_startendtag(self, tag, attrs):
        if self.mode != 'silent':
            print "Start/End tag  :", tag
            for attr in attrs:
                print "     attr:", attr
        t = Tag()
        self.depth = self.depth + 1
        t.name = tag
        t.depth = self.depth
        t.closed = 1

        if self.previous_tag == 'start':
            # current tag is first child of the last tag
            t.parent = self.tag_list[len(self.tag_list)-1]
            self.tag_list[len(self.tag_list)-1].first_child = t
        elif self.previous_tag == 'startend':
            # current tag is next sibling of last tag
            t.parent = self.tag_list[len(self.tag_list)-1].parent
            self.tag_list[len(self.tag_list)-1].next_sibling = t
        elif self.previous_tag == 'end':
            #current tag is next sibling of a previous tag of depth=self.depth
            for x in reversed(self.tag_list):
                if x.depth == self.depth:
                    x.next_sibling = t
                    if t.parent == 0:
                        t.parent = x.parent
                    break

        self.tag_list.append(t)
        self.depth = self.depth - 1
        self.previous_tag = 'startend'

    def handle_data(self, data):
        if self.mode != 'silent':
            print "Data     :", data

        self.depth = self.depth + 1

        # add data to last tag in list with depth = current depth - 1
        for x in reversed(self.tag_list):
            if x.depth == self.depth - 1:
                x.text = (x.text + ' ' + data.strip(' \n\t')).strip(' \n\t')
                break

        self.depth = self.depth - 1

    def handle_comment(self, data):
        if self.mode != 'silent':
            print "Comment  :", data

    def handle_entityref(self, name):
        if self.mode != 'silent':
            c = unichr(name2codepoint[name])
            print "Named ent:", c

    def handle_charref(self, name):
        if self.mode != 'silent':
            if name.startswith('x'):
                c = unichr(int(name[1:], 16))
            else:
                c = unichr(int(name))
            print "Num ent  :", c

    def handle_decl(self, data):
        if self.mode != 'silent':
            print "Decl     :", data

    def print_tag_list(self, u):
        for l in self.tag_list:
            print l.get_tag_info_str()

    def clear_tag_list(self):
        self.tag_list.__delslice__(0, len(self.tag_list))

    def pretty_print_tags(self):
        for t in self.tag_list:
            s = ''
            s = s + self.get_indent_str(t.depth-1)
            s = s + self.get_tag_str(t.name)
            print s

    def get_indent_str(self, n):
        s = ''
        while(n != 0):
            s = s + '    '
            n = n - 1
        return s

    def get_tag_str(self, name):
        return '<{}>'.format(name)

    def find_first_tag(self, name):
        r = 0
        for t in self.tag_list:
            if t.name == name:
                r = t
                break
        return r

    def print_first_tag_info(self, name):
        t = self.find_first_tag(name)
        if t == 0:
            print "Tag: {} not found".format(name)
        else:
            print t.get_tag_info_str()