import getopt
import sys


def flask_run(app, host='0.0.0.0', port=5000, threaded=False, debug=False):
    options, args = getopt.gnu_getopt(sys.argv, 'dh:p:t',
                                      ["debug", "host=", "threaded", "port="])

    for o, a in options:
        if o in ("--debug", "-d"):
            debug = True
        elif o in ("-h", "--host"):
            host = a
        elif o in ("-p", "--port"):
            port = a
        elif o in ("-t", "--threaded"):
            threaded=True

    print("Started execution of Social Quiz")
    print("Debug: %s" % debug)
    print("Host: %s:%s" % (host, port))
    print("Threaded: %s" % debug)

    app.run(debug=debug, host=host, port=port, threaded=threaded)
