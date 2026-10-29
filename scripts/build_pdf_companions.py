"""Render a checked Markdown teaching document without changing its wording.

Uses Pandoc only to parse Markdown. ReportLab lays out the PDF. Unsupported
constructs fail rather than silently dropping source content.
"""
import argparse
import hashlib
import html
import json
import posixpath
import re
import subprocess
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle,
    ListFlowable, ListItem, HRFlowable, XPreformatted, Image, CondPageBreak, KeepTogether,
)

# Match the existing research-companion editions. Set ANCHOR_PDF_FONT_DIR on other systems.
import os
FONTROOT = Path(os.environ.get('ANCHOR_PDF_FONT_DIR', '/System/Library/Fonts/Supplemental'))
for name, filename in [
    ('Body', 'Georgia.ttf'), ('BodyBold', 'Georgia Bold.ttf'),
    ('BodyItalic', 'Georgia Italic.ttf'), ('BodyBoldItalic', 'Georgia Bold Italic.ttf'),
    ('Sans', 'Arial.ttf'), ('SansBold', 'Arial Bold.ttf'),
    ('SansItalic', 'Arial Italic.ttf'), ('SansBoldItalic', 'Arial Bold Italic.ttf'),
    ('Mono', 'Courier New.ttf'),
]:
    pdfmetrics.registerFont(TTFont(name, str(FONTROOT / filename)))
pdfmetrics.registerFontFamily('Body', normal='Body', bold='BodyBold', italic='BodyItalic', boldItalic='BodyBoldItalic')
pdfmetrics.registerFontFamily('Sans', normal='Sans', bold='SansBold', italic='SansItalic', boldItalic='SansBoldItalic')

INK = colors.HexColor('#172635')
TEAL = colors.HexColor('#07566b')
MUTED = colors.HexColor('#53636c')
LIGHT = colors.HexColor('#edf3f5')
WIDTH, HEIGHT, MARGIN = 612, 792, 49
CONTENT = WIDTH - 2 * MARGIN

styles = {
    'body': ParagraphStyle('body', fontName='Body', fontSize=10.5, leading=15.2,
                           textColor=INK, spaceAfter=8, splitLongWords=True),
    'title': ParagraphStyle('title', fontName='SansBold', fontSize=23, leading=28,
                            textColor=INK, spaceAfter=16, keepWithNext=True),
    'h2': ParagraphStyle('h2', fontName='SansBold', fontSize=15, leading=19,
                         textColor=TEAL, spaceBefore=17, spaceAfter=9, keepWithNext=True),
    'h3': ParagraphStyle('h3', fontName='SansBold', fontSize=11.5, leading=15,
                         textColor=INK, spaceBefore=10, spaceAfter=5, keepWithNext=True),
    'small': ParagraphStyle('small', fontName='Sans', fontSize=8.3, leading=11.2,
                            textColor=MUTED, spaceAfter=6, splitLongWords=True),
    'cell': ParagraphStyle('cell', fontName='Sans', fontSize=9, leading=12.5,
                           textColor=INK, spaceAfter=3, splitLongWords=True),
    'headcell': ParagraphStyle('headcell', fontName='SansBold', fontSize=9, leading=12.5,
                               textColor=colors.white, spaceAfter=3, splitLongWords=True),
    'code': ParagraphStyle('code', fontName='Mono', fontSize=8.4, leading=11.5,
                           textColor=INK, spaceAfter=8),
}

# Avoid a single stranded line at either end of a page.
for style in styles.values():
    style.allowWidows = 0
    style.allowOrphans = 0

MATH = {'alpha':'α','beta':'β','gamma':'γ','delta':'δ','epsilon':'ε','theta':'θ',
        'lambda':'λ','mu':'μ','pi':'π','rho':'ρ','sigma':'σ','tau':'τ','phi':'φ',
        'Delta':'Δ','Sigma':'Σ','leq':'≤','geq':'≥','ne':'≠','neq':'≠','times':'×',
        'pm':'±','to':'→','infty':'∞','approx':'≈','sum':'Σ','cdot':'·'}

SUPER = dict(zip('⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺⁼⁽⁾ᵀ', '0123456789-+=()T'))
def escaped_text(value):
    # Georgia lacks the superscript minus and transpose glyphs. Render real
    # superscripts rather than embedding an invisible .notdef character.
    output=[]
    body_glyphs=pdfmetrics.getFont('Body').face.charToGlyph
    sans_glyphs=pdfmetrics.getFont('Sans').face.charToGlyph
    for c in value:
        if c in SUPER:
            output.append('<super>'+SUPER[c]+'</super>')
        elif ord(c) not in body_glyphs:
            if ord(c) not in sans_glyphs:
                raise ValueError('No supported glyph for '+repr(c))
            output.append('<font name="Sans">'+escape(c)+'</font>')
        else:
            output.append(escape(c))
    return ''.join(output)

class Renderer:
    def __init__(self, source, repo):
        self.source, self.repo, self.notes = source, repo, []
        self.title = 'Educational companion'

    def link(self, target):
        if re.match(r'^(?:https?://|mailto:|#)', target): return target
        path = posixpath.normpath('education/' + target)
        return f'https://github.com/patrickiben/{self.repo}/blob/main/{path}'

    def inlines(self, nodes):
        output = []
        for n in nodes:
            kind, c = n['t'], n.get('c')
            if kind == 'Str': output.append(escaped_text(c))
            elif kind in ('Space','SoftBreak'): output.append(' ')
            elif kind == 'LineBreak': output.append('<br/>')
            elif kind in ('Emph','Strong','Strikeout','Superscript','Subscript','SmallCaps'):
                tags = {'Emph':'i','Strong':'b','Strikeout':'strike','Superscript':'super','Subscript':'sub','SmallCaps':'span'}
                tag = tags[kind]
                output.append(self.inlines(c) if tag == 'span' else f'<{tag}>{self.inlines(c)}</{tag}>')
            elif kind == 'Code': output.append('<font name="Mono" size="9">' + escape(c[1]) + '</font>')
            elif kind == 'Math':
                value = re.sub(r'\\([A-Za-z]+)', lambda m:MATH.get(m[1], '\\'+m[1]), c[1])
                if '\\' in value or re.search(r'[{}]', value): raise ValueError('Unsupported equation: '+c[1])
                output.append(escaped_text(value))
            elif kind == 'Link':
                output.append('<link href="'+html.escape(self.link(c[2][0]), quote=True)+'" color="#07566b">'+self.inlines(c[1])+'</link>')
            elif kind == 'Quoted': output.append('“'+self.inlines(c[1])+'”')
            elif kind == 'Span': output.append(self.inlines(c[1]))
            elif kind == 'Cite': output.append(self.inlines(c[1]))
            elif kind == 'Note':
                self.notes.append(c); output.append(f'<super>{len(self.notes)}</super>')
            elif kind == 'RawInline':
                if c[0] == 'html' and c[1] in ('<br>','<br/>','<br />'): output.append('<br/>')
                else: raise ValueError('Unsupported inline: '+repr(n))
            elif kind == 'Image': raise ValueError('Inline images need explicit figure layout')
            else: raise ValueError('Unknown inline: '+repr(n))
        return ''.join(output)

    def paragraph(self, nodes, style='body'):
        paragraph = Paragraph(self.inlines(nodes), styles[style])
        if len(nodes)==1 and nodes[0]['t']=='Strong':
            paragraph.keepWithNext = True
        if nodes and nodes[0]['t']=='Strong' and self.inlines(nodes[0]['c'])=='Source:':
            # Keep a detailed unit's source label with its opening explanation.
            paragraph.keepWithNext = True
        return paragraph

    def table(self, content):
        attr, caption, specs, head, bodies, foot = content
        rows = head[1][:]
        for body in bodies: rows.extend(body[2] + body[3])
        rows.extend(foot[1])
        data = []
        for i, row in enumerate(rows):
            cells = []
            for cell in row[1]:
                if cell[2] != 1 or cell[3] != 1: raise ValueError('Spanning table cells require explicit review')
                cells.append(self.blocks(cell[4], 'headcell' if i < len(head[1]) else 'cell'))
            data.append(cells)
        if not data: return []
        ncol = len(data[0]); assert all(len(row)==ncol for row in data)
        # Content-dependent widths keep short labels from crowding explanations.
        weights=[]
        for j in range(ncol):
            lengths=[sum(len(getattr(x,'text','')) for x in row[j]) for row in data]
            weights.append(max(12, min(85, (sum(lengths)/len(lengths))**0.58*6)))
        widths=[CONTENT*w/sum(weights) for w in weights]
        t=Table(data,colWidths=widths,repeatRows=len(head[1]),hAlign='LEFT',spaceBefore=4,spaceAfter=12)
        cmds=[('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,0),(-1,-1),0.3,colors.HexColor('#d5dfe4'))]
        if head[1]: cmds.append(('BACKGROUND',(0,0),(-1,len(head[1])-1),TEAL))
        for i in range(len(head[1]),len(data)):
            if i%2==0: cmds.append(('BACKGROUND',(0,i),(-1,i),LIGHT))
        t.setStyle(TableStyle(cmds)); return [t]

    def blocks(self, nodes, style='body'):
        output=[]
        for node_index,node in enumerate(nodes):
            kind,c=node['t'],node.get('c')
            if kind in ('Para','Plain'): output.append(self.paragraph(c,style))
            elif kind == 'Header':
                level,attr,words=c
                if level==2: output.append(CondPageBreak(110))
                elif level>=3 and not re.match(r'^[A-Z]\d+\.', re.sub('<[^>]+>','',self.inlines(words))):
                    output.append(CondPageBreak(80))
                if level==1 and self.title=='Educational companion':
                    self.title=re.sub('<[^>]+>','',self.inlines(words)); key='title'
                else: key='h2' if level<=2 else 'h3'
                p=Paragraph('<a name="'+html.escape(attr[0],quote=True)+'"/>'+self.inlines(words),styles[key])
                if node_index+1<len(nodes) and nodes[node_index+1]['t']=='Table':
                    # A long table must split into available page space rather
                    # than moving as one keep-with-next group. The conditional
                    # break above reserves room for the heading and first rows.
                    p.keepWithNext=False
                p.outline=(min(level-1,2),attr[0],re.sub('<[^>]+>','',self.inlines(words)))
                output.append(p)
            elif kind in ('BulletList','OrderedList'):
                items=c if kind=='BulletList' else c[1]
                count=1 if kind=='BulletList' else c[0][0]
                children=[ListItem(self.blocks(x,style),leftIndent=0) for x in items]
                output.append(ListFlowable(children,bulletType='bullet' if kind=='BulletList' else '1',start=count if kind=='OrderedList' else 'circle',leftIndent=17,bulletFontName='Sans',bulletFontSize=8,spaceAfter=7))
            elif kind=='Table': output.extend(self.table(c))
            elif kind=='BlockQuote':
                output.extend(self.blocks(c,style)); output.append(Spacer(1,3))
            elif kind=='HorizontalRule': output.append(HRFlowable(width='100%',thickness=.5,color=colors.HexColor('#c8d6db'),spaceBefore=8,spaceAfter=10))
            elif kind=='CodeBlock': output.append(XPreformatted(escape(c[1]),styles['code']))
            elif kind=='Div':
                children=self.blocks(c[1],style)
                if 'quiz-item' in c[0][1]: output.append(KeepTogether(children))
                else: output.extend(children)
            elif kind=='DefinitionList':
                for term,defs in c:
                    output.append(Paragraph('<b>'+self.inlines(term)+'</b>',styles[style]))
                    for definition in defs:output.extend(self.blocks(definition,style))
            else: raise ValueError('Unsupported block: '+repr(node)[:200])
        return output

class CompanionPDF(BaseDocTemplate):
    def __init__(self,path,title,source_hash):
        super().__init__(str(path),pagesize=(WIDTH,HEIGHT),leftMargin=MARGIN,rightMargin=MARGIN,topMargin=49,bottomMargin=46,title=title,author='Patrick Iben',subject='Educational companion; source SHA-256 '+source_hash,pageCompression=1,invariant=1)
        self.display_title=title;self.last_outline_level=0
        self.addPageTemplates(PageTemplate(id='content',frames=[Frame(MARGIN,46,CONTENT,HEIGHT-95,id='main',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPage=self.page))
    def page(self,canvas,doc):
        canvas.saveState();canvas.setFillColor(MUTED);canvas.setFont('Sans',8)
        if doc.page>1:
            title=self.display_title
            while pdfmetrics.stringWidth(title,'Sans',8)>CONTENT: title=title[:-2]
            canvas.drawString(MARGIN,HEIGHT-28,title)
        canvas.setStrokeColor(colors.HexColor('#c8d6db'));canvas.setLineWidth(.4);canvas.line(MARGIN,33,WIDTH-MARGIN,33)
        canvas.drawString(MARGIN,21,'Educational companion  |  Patrick Iben')
        canvas.drawRightString(WIDTH-MARGIN,21,str(doc.page));canvas.restoreState()
    def afterFlowable(self,flowable):
        if hasattr(flowable,'outline'):
            level,key,title=flowable.outline
            level=min(level,self.last_outline_level+1)
            self.canv.bookmarkPage(key);self.canv.addOutlineEntry(title,key,level=level,closed=False)
            self.last_outline_level=level

def main():
    parser=argparse.ArgumentParser(description="Render the two research and teaching PDF editions. Requires ReportLab, pypdf, Pandoc and Georgia/Arial fonts.")
    parser.add_argument('--check',action='store_true',help='verify source and PDF hashes against the build receipt')
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    metadata_path=root/'education/pdf_build_metadata.json'
    if args.check:
        data=json.loads(metadata_path.read_text())
        for record in data['editions']:
            for kind in ('markdown','pdf'):
                path=root/record[kind]['path']
                assert hashlib.sha256(path.read_bytes()).hexdigest()==record[kind]['sha256'],str(path)+' changed'
        print('Both PDF editions match their checked Markdown sources and build receipt.')
        return
    from pypdf import PdfReader
    receipt={'format':'research-companion-pdf-build-v1','date':'2026-10-29','style':'Research and teaching series: Georgia body, Arial headings, teal accents, letter pages','editions':[], 'manuscript_source':json.loads((root/'docs/learning.json').read_text())['source']}
    for stem in ('STUDY_GUIDE','COMPANION'):
        # The concise edition uses slightly tighter paragraph spacing to avoid
        # an almost empty final page, while retaining the series typography.
        styles['body'].spaceAfter=6 if stem=='STUDY_GUIDE' else 8
        styles['h2'].spaceBefore=15 if stem=='STUDY_GUIDE' else 17
        md=root/'education'/f'{stem}.md'; pdf=md.with_suffix('.pdf')
        digest=hashlib.sha256(md.read_bytes()).hexdigest()
        ast=json.loads(subprocess.check_output(['pandoc',str(md),'-f','gfm+tex_math_dollars+footnotes','-t','json']))
        # Keep a question, its choices and explained answer on the same page.
        grouped=[];index=0
        while index<len(ast['blocks']):
            node=ast['blocks'][index]
            if node['t']=='Header' and re.match(r'^t\d{2}',node['c'][1][0]):
                section=[node];index+=1
                while index<len(ast['blocks']) and ast['blocks'][index]['t']!='Header':
                    section.append(ast['blocks'][index]);index+=1
                grouped.append({'t':'Div','c':[['',['quiz-item'],[]],section]})
            else: grouped.append(node);index+=1
        renderer=Renderer(md,'contact-map-anchor-audit');story=renderer.blocks(grouped)
        if renderer.notes:
            raise ValueError('Footnotes need a dedicated review before publishing')
        CompanionPDF(pdf,renderer.title,digest).build(story)
        pages=len(PdfReader(pdf).pages)
        receipt['editions'].append({'name':stem,'pages':pages,'markdown':{'path':str(md.relative_to(root)),'sha256':digest},'pdf':{'path':str(pdf.relative_to(root)),'sha256':hashlib.sha256(pdf.read_bytes()).hexdigest()}})
    metadata_path.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
