from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfgen import canvas
from reportlab.platypus import PageTemplate, BaseDocTemplate, PageBreak, Flowable, Image
from reportlab.lib.colors import *
from reportlab.platypus.frames import Frame

# we know some glyphs are missing, suppress warnings
import reportlab.rl_config
reportlab.rl_config.warnOnMissingFontGlyphs = 0
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont('PosterBold', 'SansPosterBold.ttf'))
pdfmetrics.registerFont(TTFont('OS_CondBold', 'OpenSans-CondBold.ttf'))
pdfmetrics.registerFont(TTFont('OS_CondLight', 'OpenSans-CondLight.ttf'))
pdfmetrics.registerFont(TTFont('OS_CondLightItalic', 'OpenSans-CondLightItalic.ttf'))


import subprocess

SLIDE_HEIGHT, SLIDE_WIDTH = 7.5*inch, 10*inch
#print(SLIDE_HEIGHT, SLIDE_WIDTH, inch)
#540.0, 720.0, 72.0

class SlideDocTemplate(BaseDocTemplate):
    """
    Template for a document containing multiple slides.
    """
    def __init__(self, filename, **kw):
        self.allowSplitting = 0
        BaseDocTemplate.__init__(self, filename, **kw)
        self.pagesize = (SLIDE_WIDTH,SLIDE_HEIGHT)

        # padding defaults to 6 on each side
        #Frame(x1, y1, width,height, leftPadding=6, bottomPadding=6, rightPadding=6,
        #topPadding=6, id=None, showBoundary=0)
        slide_frame = Frame(0, 0, SLIDE_WIDTH,SLIDE_HEIGHT,
                            leftPadding=0,
                            bottomPadding=0,
                            rightPadding=0,
                            topPadding=0,
                            id='SlideContent', showBoundary=0)
        slide_template = PageTemplate('normal', frames=slide_frame)
        self.addPageTemplates(slide_template)

class Slide(Flowable):
    """
    Content for a single slide. 
    """
    def __init__(self):
        self.width = SLIDE_WIDTH
        self.height = SLIDE_HEIGHT
        
    def wrap(self, *args):
        availWidth, availHeight = self.width, self.height
        return (availHeight, availWidth)

    def draw(self):
        pass

class AwardSlide(Flowable):#Slide):
    """
    Content for a single award slide. 
    """
    def __init__(self, award, winner, comments):
        #Slide.__init__(self)
        Flowable.__init__(self)
        self.award = award
        self.winner = winner
        self.comments = comments
        self.width = SLIDE_WIDTH
        self.height = SLIDE_HEIGHT
        self.cent_x = self.width/2
        self.cent_y = self.height/2
        
    def wrap(self, *args):
        availWidth, availHeight = self.width, self.height
        return (availWidth, availHeight)
    
    def draw(self):
        canvas = self.canv

        ## background
        canvas.setFillColor(black)
        canvas.setStrokeColor(black)
        canvas.rect(0,0,self.width, self.height, fill=1)


        # laurel leaves
        canvas.drawImage('./leaves_left.jpg', 0, self.cent_y-0.5*inch, width=2*inch,height=4*inch,mask=None)
        canvas.drawImage('./leaves_right.jpg', self.width-2*inch, self.cent_y-0.5*inch, width=2*inch,height=4*inch,mask=None)


        ## winner + award
        canvas.setFillColor(white)
        canvas.setStrokeColor(white)
        
        canvas.setFont('PosterBold', 30)
        self.drawCentredStringWithWrap(canvas, self.winner, self.cent_x, self.height-2*inch, 24, 0.5*inch)

        canvas.line(self.cent_x-inch, self.height-3*inch, self.cent_x+inch, self.height-3*inch)

        canvas.setFont("Helvetica", 20)
        self.drawCentredStringWithWrap(canvas, self.award, self.cent_x, self.height-4*inch, 24, 0.25*inch)

        ## comments
        canvas.setFont('OS_CondLightItalic', 18)
        divisions = self.cent_y /(len(self.comments[:4])+2)
        for i, quote in enumerate(self.comments[:4]):
            canvas.drawCentredString(self.cent_x, self.cent_y-(2+i)*divisions-10, "\""+quote+"\"")


        
        
    def drawCentredStringWithWrap(self, canvas, text, x, y, max_str_width, text_height):
        if len(text) <= max_str_width :
            canvas.drawCentredString(x, y, text)
        elif len(text) > max_str_width :
            tokens = text.split(" ")
            split_index = int(math.floor(len(tokens)/2.0))
            part_one = " ".join( tokens[:split_index] )
            part_two = " ".join( tokens[split_index:] )
            offset = text_height/2
            canvas.drawCentredString(x, y+offset, part_one)
            if len(part_two) <= max_str_width :
                canvas.drawCentredString(x, y-offset, part_two)
            else:
                tokens = part_two.split(" ")
                split_index = int(math.floor(len(tokens)/2.0))
                part_one = " ".join( tokens[:split_index] )
                part_two = " ".join( tokens[split_index:] )
                offset = text_height/2
                canvas.drawCentredString(x, y-offset, part_one)
                canvas.drawCentredString(x, y-3*offset, part_two)
                #this should be recursive. Eh.
            
 
if __name__ == "__main__":

    doc = SlideDocTemplate("slides.pdf")

    doc_content_list = []

    a = AwardSlide(award="Gracious Professionalism from A Young Adult Mentor", winner="Saint Baltimore School of West Uppermost Centerbrookville",
                   comments=["good", "aw yea! They did the thing. Awesome!", "is that Latin?", "Lorem ipsum dolor sit amet, arcu arcu ligula metus, feugiat nulla congue."])
    doc_content_list.append(a)

    a = AwardSlide(award="This Team Built a Transformer", winner="St. Mary's School For Gifted Children",
                   comments=["good", "Most of the comments are just 'good'. But at least they are no longer than a Tweet.", "	Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."])
    doc_content_list.append(a)
    
    doc.build(doc_content_list)

    try:
        subprocess.Popen(["slides.pdf"], shell=True)

    except IOError:
        print 'The file is already OPENED!'
