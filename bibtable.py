import os, sys, re, csv, argparse
import bibtexparser as bib

class BibTable:
  '''
  Object corresponding to files for one .
  '''
  def __init__(self,indir,verbose=False):
    self.fmts      = ['html','tex']
    self.verbose   = verbose
    self.indir     = indir
    self.bibfile   = ''
    self.csvfile   = ''
    self.templates = {'table':dict((fmt,None) for fmt in self.fmts),\
                      'entry':dict((fmt,None) for fmt in self.fmts)}
    self.index()
    
  def index(self):
    if not os.path.isdir(self.indir):
      error("Cannot find INDIR directory: "+self.indir)
    for root,dirs,files in os.walk(self.indir):
      for file in files:
        if os.path.splitext(file)[1] == '.bib':
          if self.bibfile == '':
            self.bibfile = os.path.join(root,file)
            vupdate("Found bibfile: "+self.bibfile,self.verbose)
          else:
            error("More than one .bib file found.")
        if os.path.splitext(file)[1] == '.csv':
          if self.csvfile == '':
            self.csvfile = os.path.join(root,file)
            vupdate("Found csvfile: "+self.csvfile,self.verbose)
          else:
            error("More than one .csv file found.")
        for fmt in self.fmts:
          for tmp in self.templates.keys():
            if file == tmp+'.'+fmt:
              self.templates[tmp][fmt] = Template(tmp,os.path.join(root,file))
              vupdate("Found template: "+tmp+"."+fmt,self.verbose)

  def csv_to_bib(self,task):
    if task == 'add':
      update("Adding tags: "+self.csvfile+" -> "+self.bibfile)
    if task == 'rem':
      update("Removing tags: "+self.csvfile+" -> "+self.bibfile)
    if self.csvfile is '':
      error("Please provide a csvfile in INDIR")
    if self.bibfile is '':
      error("Please provide a bibfile in INDIR")
    vupdate("Loading bibfile...",self.verbose)
    with open(self.bibfile) as fb:
      bibdata = bib.load(fb)
    vupdate("Loading csvfile...",self.verbose)
    csvlist = []
    with open(self.csvfile) as fc:
      reader = csv.DictReader(fc,delimiter=',')
      for entry in reader:
        csvlist.append(entry)
    vupdate("Adding tags...",self.verbose)
    for entry in csvlist:
      vupdate("- "+entry['id'],self.verbose)
      for key,value in entry.iteritems():
        if entry['id'] in bibdata.entries_dict:
          if task == 'add':
            bibdata.entries_dict[entry['id']].update({key:str(value)})
          if task == 'rem':
            if key in bibdata.entries_dict[entry['id']]:
              del bibdata.entries_dict[entry['id']][key]
            else:
              vupdate("  . tag "+key+" not found; skipping...",self.verbose)
        else:
          error("Paper key: "+entry['id']+" not in bibfile")
    vupdate("Updating bibfile...",self.verbose)
    with open(self.bibfile,'w') as fo:
      fo.write(bib.dumps(bibdata).encode('utf8'))
    update("Done.")

  def bib_to_table(self,fmt,outfile):
    update("Creating output table: "+self.bibfile+" -> "+outfile)
    if self.bibfile is '':
      error("Please provide a bibfile in INDIR")
    if self.templates['table'][fmt] is None:
      error("Please provide the template: table."+fmt+" in INDIR")
    if self.templates['entry'][fmt] is None:
      error("Please provide the template: entry."+fmt+" in INDIR")
    vupdate("Loading bibfile...",self.verbose)
    with open(self.bibfile) as fb:
      bibdata = bib.load(fb)
      publications = {}
      for entry in bibdata.entries_dict.values():
        publications.update({entry.get('ID'):Publication(entry,fmt)})
    vupdate("Finding keys in templates...",self.verbose)
    K = {}
    D = {}
    K['entry'],_          = find_keys(self.templates['entry'][fmt].get_content())
    K['table'],K['tlist'] = find_keys(self.templates['table'][fmt].get_content())
    D['table'] = dict.fromkeys(K['table'],[])
    D['tlist'] = dict.fromkeys(K['tlist'],[])
    for key in D['table'].keys():
      if len(key.split(':')) == 1:
        D['table'][key+':*'] = D['table'].pop(key)
    entrystr = ''
    vupdate("Creating table entries...",self.verbose)
    for id in publications.keys():
      vupdate("- "+id,self.verbose)
      D['entry'] = publications[id].dict(K['entry'])
      entrystr += self.templates['entry'][fmt].get_sub_content(D['entry'])
      Di = publications[id].dict(K['tlist'])
      for key,val in D['tlist'].iteritems():
        D['tlist'][key] = list(set(D['tlist'][key]+Di[key].split(', ')))
    vupdate("Subbing entries into the table...",self.verbose)
    for key in D['table'].keys():
      [keybase,keyfmt] = key.split(':')
      D['table'][key] = ''.join([keyfmt.replace('*',x) for x in D['tlist'][keybase]])
    D['table']['entries'] = entrystr
    vupdate("Creating outfile...",self.verbose)
    with open(outfile,'w') as fo:
      fo.write(self.templates['table'][fmt].get_sub_content(D['table']).encode('utf8'))
    update("Done.")
 
class Template:
  '''
  Structure for storing a string, or list of strings, and replacing specified
  keys in the string(s) with dynamic values.
  '''

  def __init__(self,name,src):
    self.name = name
    self.src  = src
    self.load_content()
  
  def get_content(self):
    return self.content

  def load_content(self):
    '''
    Load the intial content for this template from the associated file.
    '''
    with open(self.src,'r') as f:
      self.content = f.read()

  def get_sub_content(self, dic):
    '''
    Get self.content and do some substitutions without modifying this instance.
    '''
    # check for same broadcast size, if any
    # i.e. do we need to write the same value to several keys?
    argsizes = list(set([listlen(value) for key,value in dic.iteritems()]))
    assert len(argsizes) <= 2
    N = max(argsizes)
    # initial copying for broadcast
    content = [self.content[:] for i in range(N)]
    for key, value in dic.iteritems():
      # broadcast the value if singular
      if listlen(value) is 1:
        value = [value for i in range(N)]
      # write the substitutions
      for i in range(N):
        content[i] = content[i].replace(make_key(key),value[i])
    content = ''.join(content)
    return content
  
  def set_sub_content(self, keys):
    '''
    Overwrite self.content in this instance with some substitutions.
    '''
    self.content = self.get_sub_content(keys)

class Publication:
  '''
  Structure for printing publication data nicely from a bib file entry.
  Implementations of formatting for latex and html
  '''
  def __init__(self,bibdata,fmt=''):
    self.data = bibdata
    self.type = bibdata.get('ENTRYTYPE')
    self.fmt  = fmt.replace('.','')
    assert any(self.fmt in f for f in ['tex','html',''])
    self.lut  = {\
      'author'  :self.print_author,\
      'title'   :self.print_title,\
      'journal' :self.print_pubin,\
      'year'    :self.print_year,\
      'anysplit':self.print_anysplit,\
      'any'     :self.print_any}
  
  def make_ital(self,str):
    '''
    Format string as italics.
    '''
    if self.fmt == 'tex':
      str = '\textit{'+str+'}'
    elif self.fmt == 'html':
      str = '<i>'+str+'</i>'
    return str
  
  def make_bold(self,str):
    '''
    Format string in bold.
    '''
    if self.fmt == 'tex':
      str = '\textbf{'+str+'}'
    elif self.fmt == 'html':
      str = '<b>'+str+'</b>'
    return str
  
  def make_link(self,str):
    '''
    Make a link to the publication using str: try doi first, then url, then give up.
    Style should be either 'tex' or 'html'
    '''
    linkstr = str
    url = self.data.get('doi')
    if url is None:
      url = self.data.get('link')
    else:
      url = 'https://dx.doi.org/'+url
    if url is not None:
      if self.fmt == 'tex':
        linkstr = '\href{'+url+'}{'+str+'}'
      elif self.fmt == 'html':
        linkstr = '<a href='+url+' target="_blank">'+str+'</a>'
    return linkstr
  
  def print_author(self,num=999):
    '''
    Print Authors in format: 'Armstrong A, Froome C, ... and Contador A'
    or if num is given, stop after num, and print 'et al.'
    '''
    authors = re.split(' and ',self.data.get('author'))
    authorstr = ''
    # walk through authors and reformat from bib format
    for i in range(0,min(len(authors),num)):
      [last,first] = re.split(', ',authors[i])
      inits = re.split(' ',first)
      if i == len(authors)-1:
        authorstr += 'and '
      authorstr += last+' '
      for init in inits:
        authorstr += init[0]+' '
      authorstr = authorstr[:-1]+', '
    # minimal management of problematic characters
    for c in ['{','}','\\','\'']:
      authorstr = authorstr.replace(c,'')
    authorstr = authorstr[:-2]
    if num < len(authors):
      authorstr += '<i> et al.</i>'
    return self.check_chars(authorstr)
  
  def print_title(self,link=False):
    '''
    Print the title; can link to the DOI/URL if link is one of 'tex' or 'html'.
    '''
    titlestr = self.data.get('title')
    if link:
      titlestr = self.make_link(titlestr,link)
    return self.check_chars(titlestr)
  
  def print_pubin(self):
    '''
    Print the publication venue in italics.
    Implemented publication types: article, inproceedings, incollection, book.
    '''
    if self.type == 'article':
      pubinstr = self.data.get('journaltitle')
    if any(self.type in t for t in ['inproceedings','incollection','book']):
      pubinstr = self.data.get('booktitle')
    if pubinstr is None:
      pubinstr = ''
    return self.check_chars(pubinstr)
  
  def print_year(self):
    '''
    Pring the year. Check both 'date' and 'year' fields.
    '''
    yearstr = self.data.get('date')
    if yearstr is not None:
      yearstr = yearstr[0:4]
    else:
      yearstr = self.data.get('year')
      if yearstr is None:
        yearstr = ''
    return self.check_chars(yearstr)
  
  def print_any(self,key):
    '''
    Print arbitrary keys in the bib file, raw.
    '''
    datastr = self.data.get(key)
    if datastr is None:
      datastr = ''
    return self.check_chars(datastr)
  
  def print_anysplit(self,key,str='*',delim=', '):
    '''
    Print arbitrary keys in the bib file, however:
    Split by delim, wrap every split result with 'pre*post', where * is the value.
    '''
    data = self.data.get(key)
    if data is not None:
      datastr = ''
      if str is not None:
        for datum in data.split(delim):
          datastr += str.replace('*',datum)
    else:
      datastr = ''
    return self.check_chars(datastr)
  
  def check_chars(self,str):
    if self.fmt == 'tex':
      chars = {'{':'\{','}':'\}','_':'\_'}
      for cold,cnew in chars.iteritems():
        str = str.replace(cold,cnew)
    return str
  
  def dict(self,keys):
    '''
    Make a dictionary of from publication data, based on keys
    '''
    specials = self.lut.keys()
    dic = {}
    for keyfmt in keys:
      kf = keyfmt.split(':')
      if kf[0] in specials:
        dic.update({keyfmt:self.lut[kf[0]]()})
      elif len(kf)>1:
        dic.update({keyfmt:self.lut['anysplit'](kf[0],kf[1])})
      else:
        dic.update({keyfmt:self.lut['any'](kf[0])})
    return dic

def make_key(str):
  '''
  Make a standard key (for finding and substituting the key with some value).
  '''
  return '__'+str+'__'

def find_keys(str):
  '''
  Find any keys in the string.
  Return full keys (formatted) and also truncated base keys.
  '''
  keys = re.findall(make_key('(.*?)'),str)
  base = [k.split(':')[0] for k in keys]
  return keys,base

def error(msg):
  print "   ERROR: "+msg+"\n   See -h option for help."
  sys.exit(1)

def update(msg):
  print " + "+msg

def vupdate(msg,verbose=False):
  if verbose:
    print " | "+msg
    
def listlen(obj):
  '''
  Hack-ish workaround for inconsistency of strings / lists of strings.
  '''
  if isinstance(obj,list):
    return len(obj)
  elif isinstance(obj,str):
    return 1
  elif isinstance(obj,unicode):
    return 1
  else:
    return 0

def get_cli():
  '''
  Define and use the command line interface.
  '''
  cli = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,\
    description=\
    'BibTable is a tool for adding custom metadata ("tags") to bibliographies\n'+\
    '\n'+\
    '  Adding .csv data to .bib file:\n'+\
    '  1. Annotate papers with custom tags in a .csv file\n'+\
    '     | Row 1: tag titles    | Col 1: "id" (citation keys)\n'+\
    '     | Row 2+: papers       | Cols 2+: tags\n'+\
    '  2. Create a .bib file of the same papers (e.g. from Mendeley)\n'+\
    '  3. Place .csv and .bib in a folder INDIR\n'+\
    '  4. Run bibtable bib+ option to add the tags to the .bib file\n'+\
    '     | Run bib- option to remove the tags from the .bib file\n'+\
    '\n'+\
    '  Generating a table.x {.html or .tex} file from a .bib file\n'+\
    '  1. Create table templates:\n'+\
    '     | table.x: [see examples]\n'+\
    '     | entry.x: [see examples]\n'+\
    '  2. Place both templates and the .bib file in INDIR\n'+\
    '  3. Run {html,tex} option to create the output file\n'+
    '     | You must specify the output filename as -o OUTFILE'+\
    '')
  cli.add_argument('INDIR', nargs=1, help=\
                   'the directory containing the user-provided files')
  cli.add_argument('TODO', choices=['bib+', 'bib-', 'html', 'tex'], help=\
                   'do something:\n'+\
                   'bib+: add tags in a csv file to a bib file\n'+\
                   'bib-: remove tags in a csv file from a bib file\n'+\
                   'html: create a html table from a bib file\n'+\
                   'tex:  create a latex table from a bib file\n')
  cli.add_argument('-o', metavar='OUTFILE', nargs=1, default=None, help=\
                   'the output file name for {html,tex} tables\n')
  cli.add_argument('-v', action='store_true', help=\
                   'verbose switch\n\n')
                   
  args = vars(cli.parse_args())
  if args['TODO'] in ['html','tex'] and args['o'] is None:
    error("For {html,tex} options, you must supply the OUTFILE name.")
  return args

if __name__ == '__main__':
  args = get_cli()
  B = BibTable(args['INDIR'][0],args['v'])
  if args['TODO'] == 'bib+':
    B.csv_to_bib('add')
  if args['TODO'] == 'bib-':
    B.csv_to_bib('rem')
  if args['TODO'] == 'html':
    B.bib_to_table('html',args['o'][0])
  if args['TODO'] == 'tex':
    B.bib_to_table('tex',args['o'][0])
    
