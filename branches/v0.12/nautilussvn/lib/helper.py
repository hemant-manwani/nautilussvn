#
# This is an extension to the Nautilus file manager to allow better 
# integration with the Subversion source control system.
# 
# Copyright (C) 2008 NautilusSvn Team
# 
# NautilusSvn is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# NautilusSvn is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with NautilusSvn;  If not, see <http://www.gnu.org/licenses/>.
#


def encode_revisions(revision_array):
    """
    Takes a list of integer revision numbers and converts to a TortoiseSVN-like
    format. This means we have to determine what numbers are consecutives and
    collapse them into a single element (see doctest below for an example).
    
    @type revision_array list of integers
    @param revision_array A list of revision numbers.
    
    @rtype string
    @return A string of revision numbers in TortoiseSVN-like format.
    
    >>> encode_revisions([4,5,7,9,10,11,12])
    '4-5,7,9-12'
    
    >>> encode_revisions([])
    ''
    
    >>> encode_revisions([1])
    '1'
    """
    
    # Let's get a couple of cases out of the way
    if len(revision_array) == 0:
        return ""
        
    if len(revision_array) == 1:
        return str(revision_array[0])
    
    # Instead of repeating a set of statements we'll just define them as an 
    # inner function.
    def append(start, last, list):
        if start == last:
            result = "%s" % start
        else: 
            result = "%s-%s" % (start, last)
            
        list.append(result)
    
    # We need a couple of variables outside of the loop
    start = revision_array[0]
    last = revision_array[0]
    current_position = 0
    returner = []
    
    while True:
        if current_position + 1 >= len(revision_array):
            append(start, last, returner)
            break;
        
        current = revision_array[current_position]
        next = revision_array[current_position + 1]
        
        if not current + 1 == next:
            append(start, last, returner)
            start = next
            last = next
        
        last = next
        current_position += 1
        
    return ",".join(returner)

def decode_revisions(string, head):
    """
    Takes a TortoiseSVN-like revision string and returns a list of integers.
    EX. 4-5,7,9-12 -> [4,5,7,9,10,11,12]
    
    Note: This function is a first draft.  It may not be production-worthy.
    """
    returner = []
    arr = string.split(",")
    for el in arr:
        if el.find("-") != -1:
            subarr = el.split("-")
            if subarr[1] == 'HEAD':
                subarr[1] = head
            for subel in range(int(subarr[0]), int(subarr[1])+1):
                returner.append(subel)
        else:
            returner.append(int(el))
            
    return returner

