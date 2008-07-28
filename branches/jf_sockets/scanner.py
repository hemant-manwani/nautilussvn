
import sys
import SocketServer
import pysvn
import pickle
import os
import time

class MyServer( SocketServer.TCPServer ):
    allow_reuse_address = True
    

class Handler( SocketServer.StreamRequestHandler ):

    def handle( self ):
        path = self.rfile.readline().strip()
        c = pysvn.Client()
        try:
            entry = c.info(path)
        except pysvn.ClientError,e:
            print e
            results = {
                    "file": path,
                    "status": None
                }
            self.wfile.write( pickle.dumps( results ) )
            return

        if entry:
            rev = entry.revision.number
            author = entry.commit_author
        else:
            rev = 0
            author = ""
        results = {
                "file" : path,
                "revision" : rev,
                "author" : author
            }

        if os.path.isdir(path):
            # We're a folder
            st = c.status(path, recurse=1)

            # Check if this folder had been added
            for x in st:
                if x["is_versioned"] and x.path == path and x.text_status == pysvn.wc_status_kind.added:
                    results["status"] = "added"
                    return

            # Check if any of the contents of the folder have been modified
            t = set([   pysvn.wc_status_kind.modified,
                        pysvn.wc_status_kind.added,
                        pysvn.wc_status_kind.deleted])
            statuses = set([s.text_status for s in st])

            if len( t & statuses ):
                results["status"] = "modified"
            else:
                if x["is_versioned"]:
                    results["status"] = "normal"
                else:
                    results["status"] = None
        else:
            # We're a file
            st = c.status(path, recurse=0)[0]
            results = {
                    "file" : path,
                    "revision" : rev,
                    "author" : author
                }

            statuses = { pysvn.wc_status_kind.modified : "modified",
                         pysvn.wc_status_kind.added: "added",
                         pysvn.wc_status_kind.conflicted: "conflicted",
                         pysvn.wc_status_kind.unversioned: None,
                         pysvn.wc_status_kind.normal: "normal" }

            results[ "status" ] = statuses[ st.text_status ]

        self.wfile.write( pickle.dumps( results ) )

server = MyServer( ("", 33333), Handler )
server.serve_forever()

