import re 

"""
    Replace in 'text' all occurences of any key in the given dictionary by 
    its corresponding value. Returns the new string.
    
    From:
        http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/81330
""" 
def strtr(dict, text): 
  # Create a regular expression  from the dictionary keys
  regex = re.compile(u"(%s)" % "|".join(map(re.escape, dict.keys())))
  # For each match, look-up corresponding value in dictionary
  return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text) 