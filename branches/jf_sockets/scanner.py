
import sys
import SocketServer
import pysvn
import pickle
import os
import time

class Handler( SocketServer.StreamRequestHandler ):

    allow_reuse_address = True

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
                if x.path == path and x.text_status == pysvn.wc_status_kind.added:
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
                results["status"] = "normal"
        else:
            results["status"] = "normal"

        self.wfile.write( pickle.dumps( results ) )

server = SocketServer.TCPServer( ("", 33333), Handler )
server.serve_forever()

